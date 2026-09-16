import logging

from datetime import timedelta

import requests

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

SEND_TIMEOUT = 5


class DooprintJob(models.Model):
    """A print job queued for a printer, with its result and a callback to whoever asked for it."""
    _name = 'dooprint.job'
    _description = 'Print Job'
    _order = 'id desc'

    name = fields.Char(string='Description', required=True, default='Print job')
    device_id = fields.Many2one('dooprint.device', string='Device', required=True, ondelete='cascade', index=True)
    printer_id = fields.Many2one('dooprint.printer', string='Printer', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='device_id.company_id', store=True)
    payload = fields.Text(string='Content', required=True,
        help="ePOS-Print request, or ZPL for label printers.")
    state = fields.Selection([
        ('queued', 'Queued'),
        ('sent', 'Delivered'),
        ('done', 'Printed'),
        ('failed', 'Failed'),
    ], string='Status', required=True, default='queued', index=True)
    error_code = fields.Char(string='Error Code', readonly=True)
    error_message = fields.Char(string='Error', readonly=True)
    sent_at = fields.Datetime(string='Delivered On', readonly=True)
    done_at = fields.Datetime(string='Finished On', readonly=True)
    duration = fields.Float(string='Duration (s)', compute='_compute_duration',
        help="From queued to finished.")
    attempts = fields.Integer(string='Attempts', default=0, readonly=True)
    # Who asked for the job, to report the result back.
    res_model = fields.Char(string='Source Model', readonly=True)
    res_id = fields.Integer(string='Source Record', readonly=True)

    @api.depends('create_date', 'done_at')
    def _compute_duration(self):
        for job in self:
            job.duration = (job.done_at - job.create_date).total_seconds() if job.done_at and job.create_date else 0.0

    @api.model
    def _enqueue(self, printer, payload, origin=None, name=None):
        """Queue a job and deliver it: right away when Odoo reaches the device, or by waking the
        device up through the bus when it picks up its own jobs. `origin` is the requesting record."""
        job = self.create({
            'name': name or (origin and origin.display_name) or self.env._('Print job'),
            'device_id': printer.device_id.id,
            'printer_id': printer.id,
            'payload': payload,
            'res_model': origin and origin._name,
            'res_id': origin and origin.id,
        })
        job._dispatch()
        return job

    def _dispatch(self):
        for job in self:
            job.attempts += 1
            if not job.device_id.paired:
                job._finish('REVOKED')
            elif job.device_id.mode == 'local':
                job._send_now()
            else:
                job.device_id._notify()

    def _send_now(self):
        """Local mode: Odoo reaches the device and sends it the request."""
        self.ensure_one()
        url = self.printer_id.epos_url
        if not url:
            return self._finish('PRINTER_NOT_REACHABLE')
        self.write({'state': 'sent', 'sent_at': fields.Datetime.now()})
        try:
            response = requests.post(url, data=self.payload.encode(), timeout=SEND_TIMEOUT)
        except requests.RequestException:
            return self._finish('PRINTER_NOT_REACHABLE')
        result = next(etree.fromstring(response.content).iter('{*}response'), None)
        if result is None:
            return self._finish('SchemaError')
        return self._finish('' if result.get('success') == 'true' else (result.get('code') or 'UNKNOWN'))

    def _error_message(self, error_code):
        """Readable message for the codes returned by printers and the device."""
        _ = self.env._
        messages = {
            'PRINTER_NOT_REACHABLE': _("The device cannot be reached: check that it is on and its address."),
            'EX_BADPORT': _("The device could not talk to the printer."),
            'TooManyRequests': _("The device queue is full."),
            'SchemaError': _("The device did not understand the request."),
            'TIMEOUT': _("The device picked up the job but did not confirm it in time."),
            'REVOKED': _("The device was unpaired before printing."),
        }
        return messages.get(error_code) or _("The device returned code %s.", error_code)

    def _finish(self, error_code):
        """Close the job and report the result to whoever asked for it."""
        self.ensure_one()
        values = {'done_at': fields.Datetime.now()}
        if error_code:
            values.update(state='failed', error_code=error_code, error_message=self._error_message(error_code))
        else:
            values.update(state='done', error_code=False, error_message=False)
        self.write(values)
        self._notify_origin()
        return self.state == 'done'

    def _notify_origin(self):
        """The requesting model may implement _dooprint_job_done(job) to follow the job progress."""
        self.ensure_one()
        if not (self.res_model and self.res_id) or self.res_model not in self.env:
            return
        record = self.env[self.res_model].browse(self.res_id).exists()
        if record and hasattr(record, '_dooprint_job_done'):
            record._dooprint_job_done(self)

    @api.model
    def _agent_take(self, device, limit=5):
        """Jobs handed over to the device; they stay delivered until it confirms.
        SKIP LOCKED leaves out rows another request is already taking, so two calls at the same
        time never hand over the same job."""
        self.env.cr.execute("""
            SELECT id FROM dooprint_job
             WHERE device_id = %s AND state = 'queued'
          ORDER BY id
             LIMIT %s
               FOR UPDATE SKIP LOCKED
        """, (device.id, limit))
        jobs = self.browse([row[0] for row in self.env.cr.fetchall()])
        payload = [{'id': job.id, 'printer': job.printer_id.identifier, 'payload': job.payload} for job in jobs]
        jobs.write({'state': 'sent', 'sent_at': fields.Datetime.now()})
        for job in jobs:
            job._notify_origin()
        return payload

    @api.model
    def _agent_ack(self, device, job_id, error_code):
        job = self.search([('id', '=', job_id), ('device_id', '=', device.id), ('state', '=', 'sent')], limit=1)
        if not job:
            return False
        job._finish(error_code or '')
        return True

    def action_open_origin(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
        }

    def action_retry(self):
        retryable = self.filtered(lambda job: job.state in ('failed', 'sent'))
        retryable.write({'state': 'queued', 'error_code': False, 'error_message': False,
                         'sent_at': False, 'done_at': False})
        for job in retryable:
            job._notify_origin()
        retryable._dispatch()
        return self.env['dooprint.device']._notification(self.env._("%s job(s) queued again.", len(retryable)))

    @api.model
    def _cron_housekeeping(self):
        """Fail delivered jobs that were never confirmed and delete old finished ones."""
        config = self.env['dooprint.config']
        now = fields.Datetime.now()
        stuck = self.search([
            ('state', '=', 'sent'),
            ('sent_at', '<', now - timedelta(minutes=config.get_int('dooprint.job_timeout_minutes'))),
        ])
        for job in stuck:
            job._finish('TIMEOUT')
        old = self.search([
            ('state', 'in', ['done', 'failed']),
            ('create_date', '<', now - timedelta(days=config.get_int('dooprint.job_retention_days'))),
        ])
        old.unlink()
        _logger.info("dooprint: %s job(s) timed out, %s deleted", len(stuck), len(old))

import json

import requests

from odoo import api, fields, models

HTTP_TIMEOUT = 15
SINGLE_COMMANDS = ('restart', 'refresh')


class DooprintCommand(models.Model):
    """A remote command for a device, delivered the same way as a print job."""
    _name = 'dooprint.command'
    _description = 'Device Command'
    _order = 'id desc'

    device_id = fields.Many2one('dooprint.device', string='Device', required=True, ondelete='cascade', index=True)
    name = fields.Selection([
        ('restart', 'Restart the service'),
        ('refresh', 'Rescan printers'),
        ('http', 'HTTP request'),
    ], string='Command', required=True)
    state = fields.Selection([
        ('queued', 'Queued'),
        ('sent', 'Delivered'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], string='Status', required=True, default='queued', index=True)
    payload = fields.Text(string='Request', readonly=True,
        help="For HTTP requests, in JSON: url, method, headers and body.")
    result = fields.Text(string='Result', readonly=True)
    # Who asked for the command, to report the result back.
    res_model = fields.Char(string='Source Model', readonly=True)
    res_id = fields.Integer(string='Source Record', readonly=True)

    @api.model
    def _send(self, device, name, payload=None, origin=None):
        """Queue a command and wake the device up. A restart or rescan already waiting is reused."""
        if name in SINGLE_COMMANDS:
            queued = self.search([('device_id', '=', device.id), ('name', '=', name), ('state', '=', 'queued')], limit=1)
            if queued:
                device._notify()
                return queued
        command = self.create({
            'device_id': device.id,
            'name': name,
            'payload': payload and json.dumps(payload, indent=2),
            'res_model': origin and origin._name,
            'res_id': origin and origin.id,
        })
        if name == 'http' and device.mode == 'local':
            # Odoo shares the device network, so it makes the request itself.
            command._run_http_here()
        else:
            device._notify()
        return command

    def _run_http_here(self):
        self.ensure_one()
        request = json.loads(self.payload or '{}')
        try:
            response = requests.request(
                request.get('method') or 'GET', request['url'],
                headers=request.get('headers') or None,
                data=(request.get('body') or '').encode(),
                timeout=HTTP_TIMEOUT,
            )
        except requests.RequestException as error:
            return self._finish(str(error), '')
        return self._finish('', json.dumps({'status': response.status_code, 'body': response.text}))

    def _finish(self, error, result):
        self.ensure_one()
        self.write({'state': 'failed' if error else 'done', 'result': error or result or 'OK'})
        self._notify_origin()
        return not error

    def _notify_origin(self):
        """The requesting model may implement _dooprint_command_done(command) to get the result."""
        self.ensure_one()
        if not (self.res_model and self.res_id) or self.res_model not in self.env:
            return
        record = self.env[self.res_model].browse(self.res_id).exists()
        if record and hasattr(record, '_dooprint_command_done'):
            record._dooprint_command_done(self)

    @api.model
    def _agent_take(self, device):
        # Same as print jobs: SKIP LOCKED so two requests never take the same command.
        self.env.cr.execute("""
            SELECT id FROM dooprint_command
             WHERE device_id = %s AND state = 'queued'
          ORDER BY id
               FOR UPDATE SKIP LOCKED
        """, (device.id,))
        commands = self.browse([row[0] for row in self.env.cr.fetchall()])
        payload = [{'id': command.id, 'name': command.name, 'payload': json.loads(command.payload or '{}')} for command in commands]
        commands.write({'state': 'sent'})
        return payload

    @api.model
    def _agent_ack(self, device, command_id, error, result=''):
        command = self.search([('id', '=', command_id), ('device_id', '=', device.id)], limit=1)
        if not command:
            return False
        command._finish(error, result)
        return True

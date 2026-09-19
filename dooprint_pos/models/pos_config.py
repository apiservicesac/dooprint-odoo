from odoo import api, models


def dooprint_url(printer):
    """Address the browser uses to send a ticket straight to a dooprint printer."""
    printer = printer.sudo()
    address = printer.device_id.address
    return f"http://{address}/p/{printer.identifier}" if printer and address else False


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def dooprint_test_info(self, printer_id):
        """Address of a printer for the settings test button, which may run before saving."""
        printer = self.env['dooprint.printer'].sudo().browse(int(printer_id)).exists()
        return {'url': dooprint_url(printer), 'payload': printer._test_payload() if printer else ''}

    @api.model
    def dooprint_test_print(self, printer_id):
        """Queue a test page through Odoo from the printer form, before saving it."""
        self.check_access('write')
        printer = self.env['dooprint.printer'].sudo().browse(int(printer_id)).exists()
        if not printer:
            return {'result': False, 'message': self.env._("Select a printer first.")}
        job = self.env['dooprint.job'].sudo()._enqueue(printer, printer._test_payload(), name=self.env._("Test page"))
        if job.state == 'failed':
            return {'result': False, 'message': job.error_message}
        return {'result': True, 'message': self.env._("Test page queued.")}

    def _dooprint_printers(self):
        """dooprint printers this point of sale may print on."""
        self.ensure_one()
        printers = self.receipt_printer_ids | self.preparation_printer_ids
        return printers.dooprint_printer_id.sudo()

    def _dooprint_print(self, printer_id, payload):
        """Queue a ticket and answer the way the POS printers expect."""
        self.ensure_one()
        printer = self._dooprint_printers().filtered(lambda p: p.id == printer_id)
        if not printer:
            return {'result': False, 'errorCode': 'PRINTER_NOT_REACHABLE',
                    'message': self.env._("This printer is not configured on this point of sale.")}
        job = self.env['dooprint.job'].sudo()._enqueue(printer, payload, name=self.env._("POS %s", self.name))
        if job.state == 'failed':
            return {'result': False, 'errorCode': job.error_code, 'message': job.error_message}
        # Queued or delivered: the device prints it as soon as it gets it.
        return {'result': True, 'errorCode': '', 'status': 0}

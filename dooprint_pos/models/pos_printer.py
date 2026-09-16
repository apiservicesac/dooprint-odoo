from odoo import api, fields, models

from .pos_config import dooprint_url


class PosPrinter(models.Model):
    _inherit = 'pos.printer'

    printer_type = fields.Selection(
        selection_add=[('dooprint', 'Use a dooprint printer')],
        ondelete={'dooprint': 'set default'})
    dooprint_printer_id = fields.Many2one(
        'dooprint.printer', string='dooprint Printer',
        domain="[('printer_type', '=', 'receipt'), '|', ('device_id.company_id', '=', False), ('device_id.company_id', '=', company_id)]")
    dooprint_url = fields.Char(string='dooprint Printer Address', compute='_compute_dooprint_url')

    @api.depends('dooprint_printer_id')
    def _compute_dooprint_url(self):
        for printer in self:
            printer.dooprint_url = dooprint_url(printer.dooprint_printer_id)

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ['dooprint_printer_id', 'dooprint_url']

    def action_dooprint_test(self):
        self.ensure_one()
        self.dooprint_printer_id.sudo().action_test_print()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'type': 'success', 'message': self.env._("Test page queued.")},
        }

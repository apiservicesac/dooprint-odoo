from odoo import api, fields, models

from .pos_config import dooprint_url

DELIVERY_SELECTION = [
    ('server', 'Through Odoo'),
    ('browser', 'From the browser'),
]


class PosPrinter(models.Model):
    _inherit = 'pos.printer'

    printer_type = fields.Selection(
        selection_add=[('dooprint', 'Use a Dooprint printer')],
        ondelete={'dooprint': 'set default'})
    dooprint_printer_id = fields.Many2one(
        'dooprint.printer', string='Dooprint Printer',
        domain="[('printer_type', '=', 'receipt')]")
    dooprint_delivery = fields.Selection(
        DELIVERY_SELECTION, string='Dooprint Delivery', required=True, default='server',
        help="Through Odoo: the POS sends the tickets to Odoo, which queues them for the device. "
             "Works from any network.\n"
             "From the browser: the POS sends them straight to the device. The browser must be on the "
             "device network and allow Local Network Access.")
    dooprint_url = fields.Char(string='Dooprint Printer Address', compute='_compute_dooprint_url')

    @api.depends('dooprint_printer_id')
    def _compute_dooprint_url(self):
        for printer in self:
            printer.dooprint_url = dooprint_url(printer.dooprint_printer_id)

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + [
            'dooprint_printer_id', 'dooprint_url', 'dooprint_delivery',
        ]

    def action_dooprint_test(self):
        self.ensure_one()
        self.dooprint_printer_id.sudo().action_test_print()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'type': 'success', 'message': self.env._("Test page queued.")},
        }

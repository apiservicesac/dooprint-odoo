from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_dooprint_printer_id = fields.Many2one(related='pos_config_id.dooprint_printer_id', readonly=False)
    pos_dooprint_delivery = fields.Selection(related='pos_config_id.dooprint_delivery', readonly=False)

    def _is_cashdrawer_displayed(self, res_config):
        return super()._is_cashdrawer_displayed(res_config) or bool(res_config.pos_dooprint_printer_id)

    @api.depends('pos_iface_print_via_proxy', 'pos_config_id', 'pos_epson_printer_ip', 'pos_other_devices',
                 'pos_dooprint_printer_id')
    def _compute_pos_iface_cashdrawer(self):
        return super()._compute_pos_iface_cashdrawer()

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # The Dooprint printer is set on the point of sale form. Settings only need to know it, so
    # saving them does not switch off the cash drawer or hide the automatic printing options.
    pos_dooprint_printer_id = fields.Many2one(related='pos_config_id.dooprint_printer_id')

    def _is_cashdrawer_displayed(self, res_config):
        return super()._is_cashdrawer_displayed(res_config) or bool(res_config.pos_dooprint_printer_id)

    @api.depends('pos_iface_print_via_proxy', 'pos_config_id', 'pos_epson_printer_ip', 'pos_other_devices',
                 'pos_dooprint_printer_id')
    def _compute_pos_iface_cashdrawer(self):
        return super()._compute_pos_iface_cashdrawer()

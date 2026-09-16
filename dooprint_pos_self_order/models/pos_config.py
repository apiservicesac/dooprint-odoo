from odoo import api, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _load_pos_self_data_fields(self, pos_config_id):
        return super()._load_pos_self_data_fields(pos_config_id) + [
            'dooprint_printer_id', 'dooprint_delivery', 'dooprint_url', 'iface_cashdrawer',
        ]

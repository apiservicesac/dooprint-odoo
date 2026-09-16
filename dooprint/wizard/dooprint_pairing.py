from odoo import api, fields, models


class DooprintPairing(models.TransientModel):
    """Shows the pairing token a device needs to connect to this database."""
    _name = 'dooprint.pairing'
    _description = 'Connect a Device'

    pairing_token = fields.Char(string='Pairing Token', readonly=True,
        help="Paste it into the Odoo tab of the device. It includes the Odoo address.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['pairing_token'] = self.env['dooprint.device']._new_pairing_string()
        return super().create(vals_list)

    def _open(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Connect a Device'),
            'res_model': 'dooprint.pairing',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

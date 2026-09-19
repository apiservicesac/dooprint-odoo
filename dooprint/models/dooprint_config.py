from odoo import api, models

# Module system parameters and their defaults.
PARAMS = {
    'dooprint.job_timeout_minutes': 5,
    'dooprint.job_retention_days': 30,
}


class DooprintConfig(models.AbstractModel):
    """Typed access to the module parameters, so keys and defaults live in one place."""
    _name = 'dooprint.config'
    _description = 'dooprint Configuration'

    @api.model
    def get_int(self, key):
        value = self.env['ir.config_parameter'].sudo().get_str(key)
        try:
            return int(value) if value else PARAMS[key]
        except ValueError:
            return PARAMS[key]

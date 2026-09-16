from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dooprint_job_timeout_minutes = fields.Integer(
        string='Delivered Job Timeout (min)', default=5,
        config_parameter='dooprint.job_timeout_minutes',
        help="A job picked up by a device and not confirmed within this time is marked as failed.")
    dooprint_job_retention_days = fields.Integer(
        string='Keep Finished Jobs (days)', default=30,
        config_parameter='dooprint.job_retention_days')

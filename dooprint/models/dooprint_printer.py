from odoo import api, fields, models


class DooprintPrinter(models.Model):
    """A printer reported by a device: USB or network."""
    _name = 'dooprint.printer'
    _description = 'Printer'
    _order = 'device_id, name'

    device_id = fields.Many2one('dooprint.device', string='Device', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='device_id.company_id', store=True)
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    identifier = fields.Char(string='Identifier', required=True, readonly=True,
        help="Id of the printer inside the device.")
    printer_type = fields.Selection([
        ('receipt', 'Receipt'),
        ('label', 'Label'),
    ], string='Type', default='receipt', readonly=True)
    connection = fields.Selection([
        ('usb', 'USB'),
        ('network', 'Network'),
    ], string='Connection', readonly=True)
    ip_address = fields.Char(string='IP Address', readonly=True)
    connected_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
    ], string='Status', readonly=True, default='connected',
        help="Connected when the device reported it in its last heartbeat.")
    device_state = fields.Selection(related='device_id.state', string='Device Status')
    epos_url = fields.Char(string='Print Address', compute='_compute_epos_url',
        help="Where Odoo sends jobs when the device is on its network.")
    job_count = fields.Integer(string='Job Count', compute='_compute_last_job')
    last_job_date = fields.Datetime(string='Last Printed', compute='_compute_last_job')
    last_job_state = fields.Selection(
        selection=lambda self: self.env['dooprint.job']._fields['state']._description_selection(self.env),
        string='Last Job Status', compute='_compute_last_job')

    _sql_constraints = [
        ('printer_unique', 'UNIQUE(device_id, identifier)', "This printer is already registered on the device."),
    ]

    @api.depends('device_id.address', 'identifier')
    def _compute_epos_url(self):
        for printer in self:
            address = (printer.device_id.address or '').strip()
            printer.epos_url = f"http://{address}/p/{printer.identifier}/cgi-bin/epos/service.cgi" if address else False

    def _compute_last_job(self):
        Job = self.env['dooprint.job']
        for printer in self:
            job = Job.search([('printer_id', '=', printer.id)], order='id desc', limit=1)
            printer.last_job_state = job.state
            printer.last_job_date = job.create_date
            printer.job_count = Job.search_count([('printer_id', '=', printer.id)])

    @api.depends('name', 'device_id.name')
    def _compute_display_name(self):
        for printer in self:
            printer.display_name = '%s / %s' % (printer.device_id.name, printer.name)

    def action_open_jobs(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('dooprint.dooprint_job_action')
        action.update(domain=[('printer_id', '=', self.id)], context={})
        return action

    def action_test_print(self):
        """Queue a test page; it travels the same way as any job."""
        for printer in self:
            self.env['dooprint.job']._enqueue(printer, printer._test_payload(), name=self.env._("Test page"))
        return self.env['dooprint.device']._notification(self.env._("Test page queued."))

    def _test_payload(self):
        self.ensure_one()
        if self.printer_type == 'label':
            return ("^XA^PW800^LL250^CF0,35^FO0,40^FB800,1,0,C^FDTEST^FS"
                    "^CF0,25^FO0,100^FB800,1,0,C^FD%s^FS^XZ" % self.name)
        return ("""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">
<text align="center" dw="true" dh="true">TEST&#10;</text>
<text align="center">%s&#10;</text>
<feed line="2" /><cut type="feed" />
</epos-print></s:Body></s:Envelope>""" % self.name)

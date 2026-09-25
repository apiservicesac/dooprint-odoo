from odoo import fields, models


class PrinterPrinter(models.Model):
    """Odoo's report printers: a report linked to a dooprint printer prints through the job queue."""
    _inherit = 'printer.printer'

    type = fields.Selection(
        selection_add=[('dooprint', 'Dooprint')],
        ondelete={'dooprint': 'set default'})
    dooprint_printer_id = fields.Many2one(
        'dooprint.printer', string='Dooprint Printer', ondelete='cascade')

    def dooprint_print_report(self, report_id, docids, data=None):
        """Render the report for the chosen printers and queue it. Called by the browser once the
        user picks the printers; the report is rendered here, with the rights of that user."""
        report = self.env['ir.actions.report'].browse(report_id)
        records = self.env[report.model].browse(docids)
        records.check_access('read')
        printers = self.filtered(lambda p: p.type == 'dooprint' and p in report.printer_ids)
        for printer in printers:
            target = printer.sudo().dooprint_printer_id
            payload = report._dooprint_payload(target, docids, data)
            self.env['dooprint.job'].sudo()._enqueue(
                target, payload,
                origin=records if len(records) == 1 else None,
                name=None if len(records) == 1 else report.name)

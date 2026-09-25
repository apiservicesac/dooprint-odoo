from odoo import api, models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def get_print_jobs(self, report_name, docids, data):
        """Add a job for dooprint printers. It carries what to print, not the rendered report: it
        is rendered on the server once the user picks the printers."""
        jobs = super().get_print_jobs(report_name, docids, data)
        report = self._get_report(report_name)
        if report.printer_ids.filtered(lambda p: p.type == 'dooprint'):
            if isinstance(docids, models.BaseModel):
                docids = docids.ids
            elif isinstance(docids, int):
                docids = [docids]
            jobs.append({'type': 'dooprint', 'report_id': report.id, 'docids': list(docids or []), 'data': data})
        return jobs

    def _dooprint_payload(self, printer, docids, data):
        """ZPL for label printers, an ePOS image of the PDF report for receipt printers."""
        self.ensure_one()
        if printer.printer_type == 'label':
            if self.report_type != 'qweb-text':
                raise UserError(self.env._("%(printer)s prints labels: it needs a ZPL report.", printer=printer.name))
            return self._render(self.report_name, docids, data=data)[0].decode()
        if self.report_type != 'qweb-pdf':
            raise UserError(self.env._("%(printer)s prints receipts: it needs a PDF report.", printer=printer.name))
        html = self._render_qweb_html(self.report_name, docids, data=data)[0].decode()
        # Same as Odoo's ePOS printers: relative URLs (barcodes, images) need a base to resolve.
        html = html.replace('<head>', f'<head><base href="{self._get_report_url()}"/>', 1)
        return self.env['dooprint.render'].epos_from_html(html)

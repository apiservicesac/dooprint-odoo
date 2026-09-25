from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class DooprintPosController(http.Controller):

    @http.route('/dooprint_pos/print', type='json', auth='user')
    def print_ticket(self, config_id, printer_id, payload):
        """Queue a ticket rendered by the POS on one of the dooprint printers of that POS."""
        config = request.env['pos.config'].browse(int(config_id)).exists()
        if not config:
            raise AccessError(request.env._("This point of sale does not exist."))
        config.check_access('read')
        return config._dooprint_print(int(printer_id), payload)

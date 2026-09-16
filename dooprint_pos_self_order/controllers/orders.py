from werkzeug.exceptions import Unauthorized

from odoo import http
from odoo.tools import consteq

from odoo.addons.pos_self_order.controllers.orders import PosSelfOrderController


class DooprintSelfOrderController(PosSelfOrderController):

    @http.route('/dooprint_pos/self_order/print', type='jsonrpc', auth='public', website=True)
    def dooprint_print(self, access_token, printer_id, payload, order_id, order_access_token):
        """Queue a ticket from the kiosk or a phone. The order must belong to this point of sale, so
        the public access token alone is not enough to print."""
        pos_config = self._verify_pos_config(access_token)
        order = pos_config.env['pos.order'].sudo().browse(int(order_id)).exists()
        if not order or order.config_id != pos_config or not consteq(order.access_token or '', order_access_token or ''):
            raise Unauthorized(pos_config.env._("This order cannot print on this point of sale."))
        return pos_config.sudo()._dooprint_print(int(printer_id), payload)

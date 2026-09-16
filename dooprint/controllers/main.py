from odoo import http
from odoo.http import request


class DooprintController(http.Controller):
    """Routes used by the dooprint device.

    Pairing happens once with the token shown by Odoo; afterwards the device uses its own token.
    Every call is started by the device, so it works just as well when Odoo is outside its network.
    """

    def _device(self, token):
        if not token:
            return None
        return request.env['dooprint.device'].sudo().search([('token', '=', token)], limit=1)

    @http.route('/dooprint/register', type='jsonrpc', auth='public', csrf=False, save_session=False)
    def register(self, pairing_token=None, device=None, printers=None):
        token = request.env['dooprint.device'].sudo()._register_device(pairing_token, device or {}, printers or [])
        if not token:
            return {'error': 'invalid_pairing_token'}
        return {'token': token}

    @http.route('/dooprint/heartbeat', type='jsonrpc', auth='public', csrf=False, save_session=False)
    def heartbeat(self, token=None, device=None, printers=None):
        record = self._device(token)
        if not record:
            return {'error': 'unknown_token'}
        record._heartbeat(device or {}, printers or [])
        return {'name': record.name, 'mode': record.mode}

    @http.route('/dooprint/jobs', type='jsonrpc', auth='public', csrf=False, save_session=False)
    def jobs(self, token=None, limit=5):
        device = self._device(token)
        if not device:
            return {'error': 'unknown_token'}
        return {
            'name': device.name,
            'jobs': request.env['dooprint.job'].sudo()._agent_take(device, limit=min(int(limit), 20)),
            'commands': request.env['dooprint.command'].sudo()._agent_take(device),
        }

    @http.route('/dooprint/ack', type='jsonrpc', auth='public', csrf=False, save_session=False)
    def ack(self, token=None, id=None, error='', kind='job', result=''):
        device = self._device(token)
        if not device:
            return {'error': 'unknown_token'}
        if kind == 'command':
            done = request.env['dooprint.command'].sudo()._agent_ack(device, int(id), error or '', result or '')
        else:
            done = request.env['dooprint.job'].sudo()._agent_ack(device, int(id), error or '')
        if not done:
            return {'error': 'unknown_id'}
        return {'ok': True}

import base64
import json

from odoo import http
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype


class RonixQualityManagerController(http.Controller):

    @staticmethod
    def _json_response(payload, status=200):
        body = json.dumps(payload)
        return request.make_response(
            body,
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Cache-Control', 'no-store'),
            ],
            status=status,
        )

    def _serialize_button(self, button):
        base_url = request.httprequest.host_url.rstrip('/')
        return {
            'id': button.id,
            'name': button.name,
            'menu_type': button.menu_type,
            'location': {
                'id': button.location_id.id,
                'name': button.location_id.name,
                'token': button.location_id.token,
            },
            'sequence': button.sequence,
            'icon_url': '%s/ronix-quality/icon/%s' % (base_url, button.id),
            'action_url': '%s%s' % (base_url, button.mobile_route),
            'mobile_route': button.mobile_route,
        }

    @http.route('/ronix-quality/api/locations', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def mobile_app_locations(self, **_kwargs):
        locations = request.env['ronix.quality.location'].sudo().search([('active', '=', True)])
        payload = {
            'success': True,
            'count': len(locations),
            'locations': [
                {
                    'id': location.id,
                    'name': location.name,
                    'token': location.token,
                    'button_count': location.button_count,
                }
                for location in locations
            ],
        }
        return self._json_response(payload)

    @http.route('/ronix-quality/api/location/<string:location_token>/buttons', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def mobile_app_location_buttons(self, location_token, menu_type=None, **_kwargs):
        location = request.env['ronix.quality.location'].sudo().search([
            ('token', '=', location_token),
            ('active', '=', True),
        ], limit=1)
        if not location:
            return self._json_response({'success': False, 'error': 'Location not found.'}, status=404)

        domain = [
            ('location_id', '=', location.id),
            ('active', '=', True),
        ]
        if menu_type in ('main', 'side'):
            domain.append(('menu_type', '=', menu_type))

        buttons = request.env['ronix.quality.button'].sudo().search(domain, order='sequence asc, id asc')
        payload = {
            'success': True,
            'location': {
                'id': location.id,
                'name': location.name,
                'token': location.token,
            },
            'count': len(buttons),
            'buttons': [self._serialize_button(button) for button in buttons],
        }
        return self._json_response(payload)

    @http.route('/ronix-quality/icon/<int:button_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def mobile_app_button_icon(self, button_id, **_kwargs):
        button = request.env['ronix.quality.button'].sudo().browse(button_id)
        if not button.exists() or not button.active or not button.location_id.active or not button.icon_image:
            return request.not_found()
        image_data = base64.b64decode(button.icon_image)
        return request.make_response(
            image_data,
            headers=[
                ('Content-Type', guess_mimetype(image_data, default='image/png')),
                ('Access-Control-Allow-Origin', '*'),
                ('Cache-Control', 'public, max-age=300'),
            ],
        )

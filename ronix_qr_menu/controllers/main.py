import base64

from odoo import http
from odoo.http import request


class QrMenuController(http.Controller):

    # --------------------------------------------------
    # Public HTTP Pages
    # --------------------------------------------------

    @http.route('/qr-menu/<int:restaurant_id>', type='http', auth='public', website=True)
    def menu_landing(self, restaurant_id, table_id=None, **kwargs):
        restaurant = request.env['qr.menu.restaurant'].sudo().browse(restaurant_id)
        if not restaurant.exists() or not restaurant.active:
            return request.not_found()

        table = None
        if table_id:
            table = request.env['qr.menu.table'].sudo().browse(int(table_id))
            if not table.exists() or table.restaurant_id.id != restaurant.id:
                table = None

        categories = request.env['qr.menu.category'].sudo().search([
            ('restaurant_id', '=', restaurant.id),
            ('active', '=', True),
        ], order='sequence, name')

        return request.render('ronix_qr_menu.qr_menu_landing', {
            'restaurant': restaurant,
            'table': table,
            'categories': categories,
        })

    @http.route('/qr-menu/<int:restaurant_id>/table/<int:table_id>', type='http', auth='public', website=True)
    def menu_table(self, restaurant_id, table_id, **kwargs):
        return self.menu_landing(restaurant_id, table_id=table_id, **kwargs)

    @http.route('/qr-menu/<int:restaurant_id>/category/<int:category_id>', type='http', auth='public', website=True)
    def menu_category(self, restaurant_id, category_id, table_id=None, **kwargs):
        restaurant = request.env['qr.menu.restaurant'].sudo().browse(restaurant_id)
        if not restaurant.exists() or not restaurant.active:
            return request.not_found()

        category = request.env['qr.menu.category'].sudo().browse(category_id)
        if not category.exists() or category.restaurant_id.id != restaurant.id:
            return request.not_found()

        table = None
        if table_id:
            table = request.env['qr.menu.table'].sudo().browse(int(table_id))
            if not table.exists() or table.restaurant_id.id != restaurant.id:
                table = None

        items = request.env['qr.menu.item'].sudo().search([
            ('category_id', '=', category.id),
            ('active', '=', True),
            ('is_available', '=', True),
        ], order='sequence, name')

        return request.render('ronix_qr_menu.qr_menu_category_page', {
            'restaurant': restaurant,
            'category': category,
            'table': table,
            'items': items,
        })

    @http.route('/qr-menu/<int:restaurant_id>/item/<int:item_id>', type='http', auth='public', website=True)
    def menu_item_detail(self, restaurant_id, item_id, table_id=None, **kwargs):
        restaurant = request.env['qr.menu.restaurant'].sudo().browse(restaurant_id)
        if not restaurant.exists() or not restaurant.active:
            return request.not_found()

        item = request.env['qr.menu.item'].sudo().browse(item_id)
        if not item.exists() or item.restaurant_id.id != restaurant.id:
            return request.not_found()

        table = None
        if table_id:
            table = request.env['qr.menu.table'].sudo().browse(int(table_id))
            if not table.exists() or table.restaurant_id.id != restaurant.id:
                table = None

        return request.render('ronix_qr_menu.qr_menu_item_detail', {
            'restaurant': restaurant,
            'item': item,
            'table': table,
        })

    @http.route('/qr-menu/ar-model/<int:item_id>', type='http', auth='public', cors='*')
    def ar_model_file(self, item_id, **kwargs):
        item = request.env['qr.menu.item'].sudo().browse(item_id)
        if not item.exists() or not item.ar_model_3d:
            return request.not_found()

        content = base64.b64decode(item.ar_model_3d)
        filename = item.ar_model_filename or 'model.glb'

        content_type = 'model/gltf-binary'
        if filename.endswith('.gltf'):
            content_type = 'model/gltf+json'

        return request.make_response(content, headers=[
            ('Content-Type', content_type),
            ('Content-Disposition', f'inline; filename="{filename}"'),
            ('Cache-Control', 'public, max-age=86400'),
        ])

    # --------------------------------------------------
    # JSON RPC Endpoints
    # --------------------------------------------------

    @http.route('/qr_menu/call_waiter', type='json', auth='public', methods=['POST'])
    def call_waiter(self, restaurant_id, table_id, call_type='waiter', custom_message='', **kwargs):
        restaurant = request.env['qr.menu.restaurant'].sudo().browse(int(restaurant_id))
        table = request.env['qr.menu.table'].sudo().browse(int(table_id))

        if not restaurant.exists() or not table.exists():
            return {'error': 'Geçersiz restoran veya masa.'}

        if table.restaurant_id.id != restaurant.id:
            return {'error': 'Masa bu restorana ait değil.'}

        call = request.env['qr.menu.waiter.call'].sudo().create({
            'restaurant_id': restaurant.id,
            'table_id': table.id,
            'call_type': call_type,
            'custom_message': custom_message or False,
        })

        return {'success': True, 'call_id': call.id}

    @http.route('/qr_menu/check_calls', type='json', auth='user', methods=['POST'])
    def check_calls(self, restaurant_id=None, last_check=None, **kwargs):
        domain = [('state', '=', 'pending')]
        if restaurant_id:
            domain.append(('restaurant_id', '=', int(restaurant_id)))

        calls = request.env['qr.menu.waiter.call'].search(domain, order='create_date desc', limit=50)

        return [{
            'id': call.id,
            'table_name': call.table_id.name,
            'restaurant_name': call.restaurant_id.name,
            'call_type': call.call_type,
            'custom_message': call.custom_message or '',
            'created': call.create_date.isoformat() if call.create_date else '',
        } for call in calls]

    @http.route('/qr_menu/acknowledge_call', type='json', auth='user', methods=['POST'])
    def acknowledge_call(self, call_id, **kwargs):
        call = request.env['qr.menu.waiter.call'].browse(int(call_id))
        if not call.exists():
            return {'error': 'Çağrı bulunamadı.'}
        call.action_acknowledge()
        return {'success': True}

    @http.route('/qr_menu/complete_call', type='json', auth='user', methods=['POST'])
    def complete_call(self, call_id, **kwargs):
        call = request.env['qr.menu.waiter.call'].browse(int(call_id))
        if not call.exists():
            return {'error': 'Çağrı bulunamadı.'}
        call.action_complete()
        return {'success': True}

import json

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError


class RonixOnlineFormController(http.Controller):

    def _get_location(self, location_token):
        return request.env['ronix.quality.location'].sudo().search([
            ('token', '=', location_token),
            ('active', '=', True),
        ], limit=1)

    def _get_template(self, location_token, form_slug):
        return request.env['ronix.online.form.template'].sudo().search([
            ('location_id.token', '=', location_token),
            ('slug', '=', form_slug),
            ('state', '=', 'published'),
            ('active', '=', True),
            ('location_id.active', '=', True),
        ], limit=1)

    def _can_edit_template(self, template):
        user = request.env.user
        return bool(template and template.with_user(user).can_edit_frontend(user=user))

    @http.route('/online-forms/<string:location_token>', type='http', auth='public', website=True, sitemap=False)
    def online_form_index(self, location_token, **_kwargs):
        location = self._get_location(location_token)
        if not location:
            return request.not_found()
        templates = request.env['ronix.online.form.template'].sudo().search([
            ('location_id', '=', location.id),
            ('state', '=', 'published'),
            ('active', '=', True),
        ], order='sequence asc, name asc')
        return request.render('ronix_online_form_manager.online_form_index_template', {
            'location': location,
            'templates': templates,
        })

    @http.route('/online-forms/<string:location_token>/<string:form_slug>', type='http', auth='public', website=True, sitemap=False)
    def online_form_page(self, location_token, form_slug, success=None, **_kwargs):
        template = self._get_template(location_token, form_slug)
        if not template:
            return request.not_found()
        return request.render('ronix_online_form_manager.online_form_page_template', {
            'template_record': template,
            'fields': template.get_frontend_fields(),
            'errors': {},
            'values': {},
            'success': bool(success),
            'can_edit_frontend': self._can_edit_template(template),
        })

    @http.route('/online-forms/<string:location_token>/<string:form_slug>/submit', type='http', auth='public', website=True, methods=['POST'], sitemap=False)
    def online_form_submit(self, location_token, form_slug, **post):
        template = self._get_template(location_token, form_slug)
        if not template:
            return request.not_found()
        result = template.build_submission_from_post(post)
        if result['errors']:
            return request.render('ronix_online_form_manager.online_form_page_template', {
                'template_record': template,
                'fields': template.get_frontend_fields(),
                'errors': result['errors'],
                'values': post,
                'success': False,
                'can_edit_frontend': self._can_edit_template(template),
            })
        request.env['ronix.online.form.submission'].sudo().create({
            'template_id': template.id,
            'value_ids': result['value_commands'],
            'payload_json': json.dumps(result['payload'], ensure_ascii=False),
        })
        return request.redirect('%s?success=1' % template.frontend_path)

    @http.route('/online-forms/<string:location_token>/<string:form_slug>/save-layout', type='json', auth='user', methods=['POST'], csrf=False)
    def online_form_save_layout(self, location_token, form_slug, layout=None, **_kwargs):
        template = self._get_template(location_token, form_slug)
        if not template:
            return {'success': False, 'error': 'Form bulunamadi.'}
        if not self._can_edit_template(template):
            return {'success': False, 'error': 'Bu formu duzenleme yetkiniz yok.'}
        try:
            template.with_user(request.env.user).apply_frontend_layout(layout or [])
        except (AccessError, ValidationError) as exc:
            return {'success': False, 'error': str(exc)}
        return {'success': True}

import json

from odoo import fields, http
from odoo.http import request


class RonixQualityProductTrackingController(http.Controller):

    def _to_float(self, value):
        if value in (None, '', False):
            return False
        try:
            return float(str(value).replace(',', '.'))
        except (TypeError, ValueError):
            return False

    def _build_form_vals(self, post):
        line_commands = request.env['ronix.quality.product.tracking.form.line'].sudo().parse_frontend_lines(
            post.get('line_payload')
        )
        tracking_date = post.get('tracking_date') or fields.Date.context_today(request.env.user)
        return {
            'tracking_date': tracking_date,
            'operator_name': post.get('operator_name') or False,
            'section_name': post.get('section_name') or False,
            'morning_buffet_time': post.get('morning_buffet_time') or False,
            'morning_hot_service_control_1': self._to_float(post.get('morning_hot_service_control_1')),
            'morning_hot_service_control_2': self._to_float(post.get('morning_hot_service_control_2')),
            'morning_cold_service_control_1': self._to_float(post.get('morning_cold_service_control_1')),
            'morning_cold_service_control_2': self._to_float(post.get('morning_cold_service_control_2')),
            'morning_cold_storage_time': post.get('morning_cold_storage_time') or False,
            'morning_cold_storage_temp': self._to_float(post.get('morning_cold_storage_temp')),
            'morning_shock_storage_temp': self._to_float(post.get('morning_shock_storage_temp')),
            'morning_environment_time': post.get('morning_environment_time') or False,
            'morning_environment_temperature': self._to_float(post.get('morning_environment_temperature')),
            'morning_environment_humidity': self._to_float(post.get('morning_environment_humidity')),
            'evening_buffet_time': post.get('evening_buffet_time') or False,
            'evening_hot_service_control_1': self._to_float(post.get('evening_hot_service_control_1')),
            'evening_hot_service_control_2': self._to_float(post.get('evening_hot_service_control_2')),
            'evening_cold_service_control_1': self._to_float(post.get('evening_cold_service_control_1')),
            'evening_cold_service_control_2': self._to_float(post.get('evening_cold_service_control_2')),
            'evening_cold_storage_time': post.get('evening_cold_storage_time') or False,
            'evening_cold_storage_temp': self._to_float(post.get('evening_cold_storage_temp')),
            'evening_shock_storage_temp': self._to_float(post.get('evening_shock_storage_temp')),
            'evening_environment_time': post.get('evening_environment_time') or False,
            'evening_environment_temperature': self._to_float(post.get('evening_environment_temperature')),
            'evening_environment_humidity': self._to_float(post.get('evening_environment_humidity')),
            'line_ids': line_commands,
        }

    @http.route('/juju-profile', type='http', auth='public', website=True, sitemap=False)
    def juju_profile_redirect(self, **_kwargs):
        profile_url = '/odoo/action-base.action_res_users_my'
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=%s' % profile_url)
        return request.redirect(profile_url)

    @http.route('/urun-izleme-formu', type='http', auth='public', website=True, sitemap=False)
    def product_tracking_form_page(self, success=None, **_kwargs):
        return request.render('ronix_quality_manager.product_tracking_form_template', {
            'success': success,
            'today': fields.Date.context_today(request.env.user),
        })

    @http.route('/urun-izleme-formu/submit', type='http', auth='public', website=True, methods=['POST'], sitemap=False)
    def submit_product_tracking_form(self, **post):
        values = self._build_form_vals(post)
        request.env['ronix.quality.product.tracking.form'].sudo().create(values)
        return request.redirect('/urun-izleme-formu?success=1')

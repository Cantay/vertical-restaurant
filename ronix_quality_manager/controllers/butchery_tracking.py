from odoo import fields, http
from odoo.http import request


class RonixQualityButcheryTrackingController(http.Controller):

    def _build_form_vals(self, post):
        line_commands = request.env['ronix.quality.butchery.tracking.form.line'].sudo().parse_frontend_lines(
            post.get('line_payload')
        )
        return {
            'tracking_date': post.get('tracking_date') or fields.Date.context_today(request.env.user),
            'operator_name': post.get('operator_name') or False,
            'line_ids': line_commands,
        }

    @http.route('/kasaphane-urun-izleme-formu', type='http', auth='public', website=True, sitemap=False)
    def butchery_tracking_form_page(self, success=None, **_kwargs):
        return request.render('ronix_quality_manager.butchery_tracking_form_template', {
            'success': success,
            'today': fields.Date.context_today(request.env.user),
        })

    @http.route('/kasaphane-urun-izleme-formu/submit', type='http', auth='public', website=True, methods=['POST'], sitemap=False)
    def submit_butchery_tracking_form(self, **post):
        request.env['ronix.quality.butchery.tracking.form'].sudo().create(self._build_form_vals(post))
        return request.redirect('/kasaphane-urun-izleme-formu?success=1')

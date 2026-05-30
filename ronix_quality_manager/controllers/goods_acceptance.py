from odoo import fields, http
from odoo.http import request


class RonixQualityGoodsAcceptanceController(http.Controller):

    @http.route('/mal-kabul-formu', type='http', auth='user', website=True, sitemap=False)
    def goods_acceptance_form_page(self, success=None, **_kwargs):
        return request.render('ronix_quality_manager.goods_acceptance_form_template', {
            'success': success,
            'today': fields.Date.context_today(request.env.user),
            'current_user_name': request.env.user.name,
        })

    @http.route('/mal-kabul-formu/submit', type='http', auth='user', website=True, methods=['POST'], sitemap=False)
    def submit_goods_acceptance_form(self, **post):
        line_commands = request.env['ronix.quality.goods.acceptance.form.line'].sudo().parse_frontend_lines(
            post.get('line_payload')
        )
        request.env['ronix.quality.goods.acceptance.form'].sudo().create({
            'operator_name': post.get('operator_name') or request.env.user.name,
            'line_ids': line_commands,
        })
        return request.redirect('/mal-kabul-formu?success=1')

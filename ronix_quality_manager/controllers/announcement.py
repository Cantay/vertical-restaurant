from odoo import http
from odoo.http import request


class RonixQualityAnnouncementController(http.Controller):

    @http.route('/duyurular/<int:announcement_id>', type='http', auth='public', website=True, sitemap=False)
    def announcement_detail(self, announcement_id, **_kwargs):
        announcement = request.env['ronix.quality.announcement'].sudo().search([
            ('id', '=', announcement_id),
            ('active', '=', True),
            ('website_published', '=', True),
        ], limit=1)
        if not announcement:
            return request.not_found()

        return request.render('ronix_quality_manager.announcement_detail_template', {
            'announcement': announcement,
        })

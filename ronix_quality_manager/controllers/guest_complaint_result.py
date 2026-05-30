from odoo import http
from odoo.http import request


class RonixQualityGuestComplaintResultController(http.Controller):

    @http.route('/misafir-sikayet-analiz-sonucu/<int:result_id>', type='http', auth='user', website=True, sitemap=False)
    def guest_complaint_result_page(self, result_id, **_kwargs):
        result = request.env['ronix.quality.guest.complaint.result'].sudo().browse(result_id)
        if not result.exists() or not result.active:
            return request.not_found()
        return request.render('ronix_quality_manager.guest_complaint_result_frontend_template', {
            'result': result,
            'payload': result.get_frontend_report_payload(),
        })

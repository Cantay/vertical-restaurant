import base64
import mimetypes

from odoo import http
from odoo.http import content_disposition, request


class RonixQualityInformationController(http.Controller):

    @http.route(
        '/ronix-quality/information/attachment/<int:attachment_id>',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def download_information_attachment(self, attachment_id, **_kwargs):
        attachment = request.env['ronix.quality.information.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()

        information = attachment.information_id
        if not information or not information.active or not information.website_published or not attachment.datas:
            return request.not_found()

        filename = attachment.datas_fname or attachment.name or 'attachment'
        data = base64.b64decode(attachment.datas)
        mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        return request.make_response(
            data,
            headers=[
                ('Content-Type', mimetype),
                ('Content-Disposition', content_disposition(filename)),
                ('Cache-Control', 'private, max-age=0, no-store'),
            ],
        )

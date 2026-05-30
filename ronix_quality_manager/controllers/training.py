import base64
import mimetypes

from odoo import http
from odoo.http import content_disposition, request


class RonixQualityTrainingController(http.Controller):

    def _get_training_attachment(self, attachment_id):
        attachment = request.env['ronix.quality.training.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return None

        training = attachment.training_id
        if not training or not training.active or not training.website_published or not attachment.datas:
            return None
        return attachment

    def _make_attachment_response(self, attachment, disposition_type='attachment'):
        filename = attachment.datas_fname or attachment.name or 'attachment'
        data = base64.b64decode(attachment.datas)
        mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        return request.make_response(
            data,
            headers=[
                ('Content-Type', mimetype),
                ('Content-Disposition', content_disposition(filename, disposition_type=disposition_type)),
                ('Cache-Control', 'private, max-age=0, no-store'),
            ],
        )

    @http.route(
        '/ronix-quality/training/attachment/<int:attachment_id>',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def download_training_attachment(self, attachment_id, **_kwargs):
        attachment = self._get_training_attachment(attachment_id)
        if not attachment:
            return request.not_found()

        return self._make_attachment_response(attachment, disposition_type='attachment')

    @http.route(
        '/ronix-quality/training/attachment/<int:attachment_id>/view',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def preview_training_attachment(self, attachment_id, **_kwargs):
        attachment = self._get_training_attachment(attachment_id)
        if not attachment:
            return request.not_found()
        return self._make_attachment_response(attachment, disposition_type='inline')

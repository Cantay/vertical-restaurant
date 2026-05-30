import base64
import json

from odoo import fields, http
from odoo.http import content_disposition, request


class RonixQualitySpreadsheetController(http.Controller):

    def _get_document(self, access_token):
        return request.env['ronix.quality.spreadsheet.document'].sudo().search([
            ('access_token', '=', access_token),
            ('active', '=', True),
        ], limit=1)

    def _json_response(self, payload, status=200):
        return request.make_response(
            json.dumps(payload),
            headers=[
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-store'),
            ],
            status=status,
        )

    @http.route('/ronix-quality/spreadsheet/<string:access_token>', type='http', auth='public', website=True, sitemap=False)
    def spreadsheet_editor(self, access_token, **_kwargs):
        document = self._get_document(access_token)
        if not document:
            return request.not_found()
        return request.render('ronix_quality_manager.spreadsheet_editor_template', {
            'document': document,
        })

    @http.route('/ronix-quality/spreadsheet/<string:access_token>/data', type='http', auth='public', methods=['GET'], csrf=False)
    def spreadsheet_data(self, access_token, **_kwargs):
        document = self._get_document(access_token)
        if not document:
            return self._json_response({'success': False, 'error': 'Document not found.'}, status=404)
        return self._json_response({
            'success': True,
            'document': {
                'id': document.id,
                'name': document.name,
                'download_url': document.download_url,
                'last_saved_on': fields.Datetime.to_string(document.last_saved_on) if document.last_saved_on else '',
                'workbook': document._get_workbook_data(),
            },
        })

    @http.route('/ronix-quality/spreadsheet/<string:access_token>/save', type='json', auth='public', methods=['POST'], csrf=False)
    def spreadsheet_save(self, access_token, workbook=None, name=None, **_kwargs):
        document = self._get_document(access_token)
        if not document:
            return {'success': False, 'error': 'Document not found.'}
        workbook = workbook or {}
        if not isinstance(workbook, dict) or not isinstance(workbook.get('sheets', []), list):
            return {'success': False, 'error': 'Invalid workbook payload.'}
        document.write({
            'name': (name or document.name or '').strip() or document.name,
            'sheet_data_json': json.dumps(workbook, ensure_ascii=False),
            'last_saved_on': fields.Datetime.now(),
        })
        export_binary = document.export_workbook_binary()
        document.with_context(skip_spreadsheet_parse=True).write({
            'upload_file': base64.b64encode(export_binary),
        })
        return {
            'success': True,
            'last_saved_on': fields.Datetime.to_string(document.last_saved_on),
        }

    @http.route('/ronix-quality/spreadsheet/<string:access_token>/download', type='http', auth='public', website=True, sitemap=False)
    def spreadsheet_download(self, access_token, **_kwargs):
        document = self._get_document(access_token)
        if not document:
            return request.not_found()
        binary_data = document.export_workbook_binary()
        filename = (document.upload_filename or document.name or 'workbook').rsplit('.', 1)[0] + '.xlsx'
        return request.make_response(
            binary_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Length', str(len(binary_data))),
                ('Content-Disposition', content_disposition(filename)),
                ('Cache-Control', 'private, max-age=0, no-store'),
            ],
        )

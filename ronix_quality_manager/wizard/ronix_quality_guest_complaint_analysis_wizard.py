from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RonixQualityGuestComplaintAnalysisWizard(models.TransientModel):
    _name = 'ronix.quality.guest.complaint.analysis.wizard'
    _description = 'Ronix Quality Guest Complaint Analysis Wizard'

    location_id = fields.Many2one('ronix.quality.location', string='Lokasyon', readonly=True)
    report_ids = fields.Many2many(
        'ronix.quality.guest.complaint.report',
        'ronix_quality_guest_complaint_analysis_report_rel',
        'wizard_id',
        'report_id',
        string='Secili Kayitlar',
        readonly=True,
    )
    date_from = fields.Date(string='Baslangic Tarihi', readonly=True)
    date_to = fields.Date(string='Bitis Tarihi', readonly=True)
    analyzed_report_count = fields.Integer(string='Kayit Sayisi', readonly=True)
    analyzed_comment_count = fields.Integer(string='Sikayet/Beğeni Sayisi', readonly=True)
    python_summary = fields.Html(string='Python Analiz Ozeti', readonly=True, sanitize=False)
    result_message = fields.Html(string='Durum', readonly=True, sanitize=False)

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        reports = self.env['ronix.quality.guest.complaint.report'].browse(self.env.context.get('active_ids', []))
        if not reports:
            return values
        payload = reports._build_analysis_payload()
        values.update({
            'location_id': payload['location_id'],
            'report_ids': [fields.Command.set(reports.ids)],
            'date_from': payload['date_from'],
            'date_to': payload['date_to'],
            'analyzed_report_count': payload['analyzed_report_count'],
            'analyzed_comment_count': payload['analyzed_comment_count'],
            'python_summary': payload['python_summary'],
        })
        return values

    def action_refresh_analysis(self):
        self.ensure_one()
        payload = self.report_ids._build_analysis_payload()
        self.write({
            'location_id': payload['location_id'],
            'date_from': payload['date_from'],
            'date_to': payload['date_to'],
            'analyzed_report_count': payload['analyzed_report_count'],
            'analyzed_comment_count': payload['analyzed_comment_count'],
            'python_summary': payload['python_summary'],
            'result_message': '<div>Python analizi yenilendi.</div>',
        })
        return self._reopen()

    def action_create_result(self):
        self.ensure_one()
        result = self._create_result_record(status='done', error_message=False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Misafir Sikayet Analiz Sonucu',
            'res_model': 'ronix.quality.guest.complaint.result',
            'res_id': result.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_result_record(self, status='done', error_message=False):
        self.ensure_one()
        payload = self.report_ids._build_analysis_payload()
        return self.env['ronix.quality.guest.complaint.result'].create({
            'name': 'Misafir Sikayet Analiz Sonucu - %s / %s' % (self.date_from or '-', self.date_to or '-'),
            'location_id': self.location_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'source_report_ids': [fields.Command.set(self.report_ids.ids)],
            'analyzed_report_count': self.analyzed_report_count,
            'analyzed_comment_count': self.analyzed_comment_count,
            'top_complaint_topics': payload['top_complaint_topics_text'],
            'grouped_complaints': payload['grouped_complaints_text'],
            'department_distribution': payload['department_distribution_text'],
            'top_likes': payload['top_likes_text'],
            'complaint_word_analysis': payload['complaint_word_analysis_text'],
            'satisfaction_word_analysis': payload['satisfaction_word_analysis_text'],
            'top_rooms_areas': payload['top_rooms_areas_text'],
            'generated_prompt': False,
            'ai_response': False,
            'python_summary': self.python_summary,
            'status': status,
            'error_message': error_message or False,
        })

    def _reopen(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Misafir Sikayet Analizi',
            'res_model': 'ronix.quality.guest.complaint.analysis.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

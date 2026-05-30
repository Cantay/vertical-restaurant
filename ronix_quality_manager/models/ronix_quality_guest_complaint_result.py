import json

from odoo import fields, models


class RonixQualityGuestComplaintResult(models.Model):
    _name = 'ronix.quality.guest.complaint.result'
    _description = 'Ronix Quality Guest Complaint Result'
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, default='Misafir Sikayet Analiz Sonucu')
    location_id = fields.Many2one('ronix.quality.location', string='Lokasyon')
    date_from = fields.Date(string='Baslangic Tarihi')
    date_to = fields.Date(string='Bitis Tarihi')
    source_report_ids = fields.Many2many(
        'ronix.quality.guest.complaint.report',
        'ronix_quality_guest_complaint_result_report_rel',
        'result_id',
        'report_id',
        string='Analiz Edilen Yorumlar',
    )
    analyzed_report_count = fields.Integer(string='Analiz Edilen Kayit')
    analyzed_comment_count = fields.Integer(string='Analiz Edilen Sikayet/Beğeni')
    top_complaint_topics = fields.Text(string='En Cok Sikayet Edilen Konular')
    grouped_complaints = fields.Text(string='Sikayet Gruplari')
    department_distribution = fields.Text(string='Departman Dagilimi')
    top_likes = fields.Text(string='En Cok Beğenilen Konular')
    complaint_word_analysis = fields.Text(string='Kelime Bazli Sikayet Analizi')
    satisfaction_word_analysis = fields.Text(string='Kelime Bazli Memnuniyet Analizi')
    top_rooms_areas = fields.Text(string='En Cok Ariza Alinan Oda/Mekanlar')
    generated_prompt = fields.Text(string='Olusturulan Prompt')
    ai_response = fields.Html(string='Yapay Zeka Sonucu', sanitize=False)
    python_summary = fields.Html(string='Python Analiz Ozeti', sanitize=False)
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    status = fields.Selection(
        [('draft', 'Taslak'), ('done', 'Tamamlandi'), ('error', 'Hata')],
        string='Durum',
        default='draft',
        required=True,
    )
    error_message = fields.Text(string='Hata Mesaji')
    active = fields.Boolean(default=True)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/misafir-sikayet-analiz-sonucu/%s' % record.id if record.id else False

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }

    def _parse_counter_text(self, text):
        rows = []
        for line in (text or '').splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            label, value = line.split(':', 1)
            digits = ''.join(char for char in value if char.isdigit())
            count = int(digits) if digits else 0
            rows.append({'label': label.strip(), 'count': count})
        return rows

    def get_frontend_report_payload(self):
        self.ensure_one()
        complaint_topics = self._parse_counter_text(self.top_complaint_topics)
        departments = self._parse_counter_text(self.department_distribution)
        likes = self._parse_counter_text(self.top_likes)
        rooms = self._parse_counter_text(self.top_rooms_areas)
        total_topic = sum(item['count'] for item in complaint_topics) or 1
        total_department = sum(item['count'] for item in departments) or 1
        total_like = sum(item['count'] for item in likes) or 1
        total_room = sum(item['count'] for item in rooms) or 1
        palette = ['#c97c5d', '#e0a96d', '#78a38b', '#6f8fb8', '#b786a4', '#d7c27c', '#8c8c8c']

        def enrich(items, total):
            enriched = []
            for index, item in enumerate(items):
                percentage = round((item['count'] / total) * 100, 2) if total else 0
                enriched.append({
                    **item,
                    'percentage': percentage,
                    'color': palette[index % len(palette)],
                })
            return enriched

        def build_chart_style(items):
            if not items:
                return 'background:#eadfd3;'
            start = 0
            segments = []
            for item in items[:6]:
                end = start + item['percentage']
                segments.append('%s %s%% %s%%' % (item['color'], start, end))
                start = end
            if start < 100:
                segments.append('#eadfd3 %s%% 100%%' % start)
            return 'background:conic-gradient(%s);' % ','.join(segments)

        payload = {
            'summary': {
                'date_from': fields.Date.to_string(self.date_from) if self.date_from else '-',
                'date_to': fields.Date.to_string(self.date_to) if self.date_to else '-',
                'analyzed_report_count': self.analyzed_report_count,
                'analyzed_comment_count': self.analyzed_comment_count,
                'location_name': self.location_id.name or '-',
            },
            'complaint_topics': enrich(complaint_topics, total_topic),
            'departments': enrich(departments, total_department),
            'likes': enrich(likes, total_like),
            'rooms': enrich(rooms, total_room),
            'python_summary': self.python_summary or '',
        }
        payload['complaint_topics_chart_style'] = build_chart_style(payload['complaint_topics'])
        payload['departments_chart_style'] = build_chart_style(payload['departments'])
        payload['likes_chart_style'] = build_chart_style(payload['likes'])
        payload['rooms_chart_style'] = build_chart_style(payload['rooms'])
        payload['complaint_topics_json'] = json.dumps(payload['complaint_topics'])
        payload['departments_json'] = json.dumps(payload['departments'])
        payload['likes_json'] = json.dumps(payload['likes'])
        payload['rooms_json'] = json.dumps(payload['rooms'])
        return payload

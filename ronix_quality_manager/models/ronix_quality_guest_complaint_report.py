import base64
import datetime
import io
import re
import zipfile
from collections import Counter
from xml.etree import ElementTree as ET

from odoo import api, fields, models
from odoo.exceptions import ValidationError


XLSX_NS = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DEFAULT_DATE_NUMFMTS = {
    14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 30, 36, 45, 46, 47, 50, 57,
}
HEADER_ALIASES = {
    'tarih': 'report_date',
    'saat': 'report_time',
    'odano': 'room_number',
    'oda no': 'room_number',
    'acente': 'agency_name',
    'dil': 'guest_language',
    'dili': 'guest_language',
    'checkin': 'checkin_date',
    'checkout': 'checkout_date',
    'originaltext': 'original_text',
    'orijinaltext': 'original_text',
    'translate': 'original_text',
    'translated text': 'original_text',
    'begeniler': 'likes_text',
    'sikayetler': 'complaints_text',
    'oneriler': 'suggestions_text',
    'istekler': 'requests_text',
    'aciklamalar': 'notes_text',
    'aciklamalar r': 'notes_text',
    'aksiyon': 'action_text',
    'turu': 'guest_type',
    'asistan': 'assistant_name',
    'tekrargelme': 'return_status',
    'tekrar gelme': 'return_status',
}


def _normalize_header(value):
    text = str(value or '').strip().lower()
    text = text.translate(str.maketrans({
        'ç': 'c',
        'ğ': 'g',
        'ı': 'i',
        'İ': 'i',
        'ö': 'o',
        'ş': 's',
        'ü': 'u',
    }))
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return ' '.join(text.split())


def _normalize_text(value):
    text = str(value or '').lower()
    text = text.translate(str.maketrans({
        'ç': 'c',
        'ğ': 'g',
        'ı': 'i',
        'İ': 'i',
        'ö': 'o',
        'ş': 's',
        'ü': 'u',
    }))
    return re.sub(r'\s+', ' ', text).strip()


STOPWORDS = {
    've', 'ile', 'bir', 'bu', 'icin', 'gibi', 'daha', 'çok', 'cok', 'ama', 'de', 'da', 'mi', 'mu',
    'misafir', 'otelimize', 'odaya', 'odaya', 'otel', 'otelimizde', 'olan', 'olarak', 'gore', 'gorevli',
    'talep', 'etti', 'edildi', 'iletildi', 'bugun', 'yazinildi', 'yazildi', 'hemen', 'beri', 'icin',
}
NEGATIVE_PHRASES = {
    'oda temizligi': 'Temizlik ve Hijyen',
    'banyo temizligi': 'Temizlik ve Hijyen',
    'havlu talebi': 'Bornoz Havlu Tekstil',
    'bornoz talebi': 'Bornoz Havlu Tekstil',
    'su akintisi': 'Teknik Ariza',
    'klima arizasi': 'Teknik Ariza',
    'elektrik arizasi': 'Teknik Ariza',
    'yemek kalitesi': 'Yiyecek Icecek',
    'glutensiz yemek': 'Yiyecek Icecek',
    'gec checkin': 'Checkin Checkout',
    'gec checkout': 'Checkin Checkout',
}
TOPIC_KEYWORDS = {
    'Temizlik ve Hijyen': ['temizlik', 'kirli', 'leke', 'cop', 'banyo', 'klozet', 'ayna', 'duvar', 'toz'],
    'Bornoz Havlu Tekstil': ['bornoz', 'havlu', 'terlik', 'yastik', 'yorgan', 'nevresim', 'carsaf'],
    'Teknik Ariza': ['ariza', 'akinti', 'su', 'klima', 'elektrik', 'ampul', 'tv', 'sifon', 'lavabo', 'dus'],
    'Yiyecek Icecek': ['restoran', 'yemek', 'kahvalti', 'glutensiz', 'tatli', 'garson', 'siparis'],
    'Gurultu ve Konfor': ['gurultu', 'ses', 'rahatsiz', 'konfor', 'uyku'],
    'Checkin Checkout': ['checkin', 'checkout', 'resepsiyon', 'giris', 'cikis'],
}
LIKE_KEYWORDS = {
    'Yiyecek Icecek Memnuniyeti': ['yemek', 'kahvalti', 'restoran', 'lezzet', 'tatli', 'icecek', 'sunum'],
    'Teknik Hizmet Cozumu': ['teknik', 'ariza', 'cozuldu', 'cozum', 'tamir', 'bakim', 'hizli cozum'],
    'Konfor ve Sessizlik': ['konfor', 'rahat', 'sessiz', 'huzurlu', 'uyku', 'gurultu yok'],
    'Checkin Checkout Deneyimi': ['checkin', 'checkout', 'resepsiyon', 'giris', 'cikis', 'karsilama'],
    'Temizlik ve Hijyen Memnuniyeti': ['temiz', 'temizlik', 'hijyen', 'piril', 'duzenli'],
    'Tekstil ve Oda Ekipmani Memnuniyeti': ['bornoz', 'havlu', 'terlik', 'yastik', 'yorgan', 'nevresim'],
    'Personel Ilgisi ve Hizmet Kalitesi': ['personel', 'ilgili', 'guleryuz', 'yardimci', 'nazik', 'profesyonel'],
}
DEPARTMENT_KEYWORDS = {
    'Kat Hizmetleri': ['temizlik', 'kirli', 'leke', 'bornoz', 'havlu', 'terlik', 'yastik', 'yorgan', 'oda temizligi'],
    'Teknik Servis': ['ariza', 'akinti', 'su', 'klima', 'elektrik', 'ampul', 'tv', 'sifon', 'lavabo', 'dus'],
    'Yiyecek Icecek': ['restoran', 'yemek', 'kahvalti', 'glutensiz', 'tatli', 'siparis'],
    'Onburo': ['checkin', 'checkout', 'resepsiyon', 'giris', 'cikis'],
    'Misafir Iliskileri': ['misafir iliskileri', 'guest relation', 'talep', 'istek'],
}
AREA_KEYWORDS = {
    'Ana Restoran': ['ana restoran', 'restoran'],
    'Oda': ['oda', 'odasi'],
    'Banyo': ['banyo'],
    'Lobi': ['lobi'],
    'Spa': ['spa'],
    'Havuz': ['havuz'],
}


class RonixQualityGuestComplaintReport(models.Model):
    _name = 'ronix.quality.guest.complaint.report'
    _description = 'Ronix Quality Guest Complaint Report'
    _order = 'report_date desc, report_time desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    report_date = fields.Date(string='Tarih')
    report_time = fields.Char(string='Saat')
    room_number = fields.Char(string='Oda No')
    agency_name = fields.Char(string='Acente')
    guest_language = fields.Char(string='Dil')
    checkin_date = fields.Date(string='Checkin')
    checkout_date = fields.Date(string='Checkout')
    original_text = fields.Text(string='Original Text')
    likes_text = fields.Text(string='Beğeniler')
    complaints_text = fields.Text(string='Şikayetler')
    suggestions_text = fields.Text(string='Öneriler')
    requests_text = fields.Text(string='İstekler')
    notes_text = fields.Text(string='Açıklamalar')
    action_text = fields.Text(string='Aksiyon')
    guest_type = fields.Char(string='Türü')
    assistant_name = fields.Char(string='Asistan')
    return_status = fields.Char(string='Tekrar Gelme')
    source_filename = fields.Char(string='Kaynak Dosya')
    active = fields.Boolean(default=True)

    def action_open_analysis_wizard(self):
        if not self:
            raise ValidationError('Analiz icin en az bir kayit secmelisiniz.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Misafir Sikayet Analizi',
            'res_model': 'ronix.quality.guest.complaint.analysis.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids},
        }

    @api.depends('report_date', 'room_number', 'agency_name')
    def _compute_name(self):
        for record in self:
            parts = [
                fields.Date.to_string(record.report_date) if record.report_date else '',
                record.room_number or '',
                record.agency_name or '',
            ]
            record.name = ' - '.join(part for part in parts if part) or 'Misafir Sikayet Kaydi'

    @api.model
    def import_from_xlsx_attachments(self, attachments, location_id=False):
        all_vals = []
        results = []
        for attachment in attachments:
            attachment_name = attachment.name or 'Excel'
            if not attachment.datas:
                results.append({
                    'filename': attachment_name,
                    'status': 'error',
                    'message': 'Dosya icerigi bos.',
                    'imported': 0,
                })
                continue
            if not attachment_name.lower().endswith('.xlsx'):
                results.append({
                    'filename': attachment_name,
                    'status': 'error',
                    'message': 'Sadece .xlsx dosyalari destekleniyor.',
                    'imported': 0,
                })
                continue
            try:
                parsed = self._read_xlsx_rows(base64.b64decode(attachment.datas))
            except Exception as exc:
                results.append({
                    'filename': attachment_name,
                    'status': 'error',
                    'message': str(exc),
                    'imported': 0,
                })
                continue
            if not parsed['matched_fields']:
                results.append({
                    'filename': attachment_name,
                    'status': 'error',
                    'message': 'Basliklar sistem alanlariyla eslesmedi.',
                    'imported': 0,
                })
                continue
            imported_count = 0
            for row in parsed['rows']:
                vals = self._prepare_import_vals(row, attachment, location_id=location_id)
                if not vals:
                    continue
                all_vals.append(vals)
                imported_count += 1
            if imported_count:
                results.append({
                    'filename': attachment_name,
                    'status': 'success',
                    'message': '%s satir eklendi.' % imported_count,
                    'imported': imported_count,
                })
            else:
                results.append({
                    'filename': attachment_name,
                    'status': 'warning',
                    'message': 'Eslesen veri satiri bulunamadi.',
                    'imported': 0,
                })
        if all_vals:
            self.create(all_vals)
        return {
            'total_imported': len(all_vals),
            'results': results,
        }

    @api.model
    def _prepare_import_vals(self, row, attachment, location_id=False):
        vals = {field_name: row.get(field_name) or False for field_name in HEADER_ALIASES.values()}
        if not any(vals.values()):
            return False
        vals['source_filename'] = attachment.name
        vals['location_id'] = location_id or self.env['ronix.quality.location']._get_single_active_location_id()
        return vals

    def _build_analysis_payload(self):
        records = self.sorted(lambda record: (record.report_date or fields.Date.today(), record.report_time or ''))
        if not records:
            raise ValidationError('Analiz icin kayit bulunamadi.')
        complaint_texts = [record.complaints_text for record in records if record.complaints_text]
        like_texts = [record.likes_text for record in records if record.likes_text]
        combined_complaints = complaint_texts
        topic_counter = self._counter_from_mapping(combined_complaints, TOPIC_KEYWORDS, fallback='Diger')
        department_counter = self._counter_from_mapping(combined_complaints, DEPARTMENT_KEYWORDS, fallback='Diger')
        likes_counter = self._counter_from_mapping(like_texts, LIKE_KEYWORDS, fallback='Diger Pozitif Baslik')
        room_area_counter = self._room_area_counter(records)
        complaint_words = self._word_counter(complaint_texts)
        like_words = self._word_counter(like_texts)
        bigram_counter = self._ngram_counter(complaint_texts, 2)
        trigram_counter = self._ngram_counter(complaint_texts, 3)
        date_values = [record.report_date for record in records if record.report_date]
        date_from = min(date_values) if date_values else False
        date_to = max(date_values) if date_values else False
        analyzed_comment_count = len(complaint_texts)
        top_complaint_topics_text = self._format_counter_lines(topic_counter)
        grouped_complaints_text = False
        department_distribution_text = self._format_percentage_lines(department_counter)
        top_likes_text = self._format_like_counter_lines(likes_counter)
        complaint_word_analysis_text = self._format_word_analysis(complaint_words, bigram_counter, trigram_counter)
        satisfaction_word_analysis_text = self._format_counter_lines(like_words, limit=20)
        top_rooms_areas_text = self._format_counter_lines(room_area_counter, limit=10)
        python_summary = self._build_python_summary_html(
            top_complaint_topics_text,
            department_distribution_text,
            top_likes_text,
            top_rooms_areas_text,
        )
        return {
            'location_id': records[:1].location_id.id,
            'date_from': date_from,
            'date_to': date_to,
            'analyzed_report_count': len(records),
            'analyzed_comment_count': analyzed_comment_count,
            'top_complaint_topics_text': top_complaint_topics_text,
            'grouped_complaints_text': grouped_complaints_text,
            'department_distribution_text': department_distribution_text,
            'top_likes_text': top_likes_text,
            'complaint_word_analysis_text': complaint_word_analysis_text,
            'satisfaction_word_analysis_text': satisfaction_word_analysis_text,
            'top_rooms_areas_text': top_rooms_areas_text,
            'python_summary': python_summary,
            'generated_prompt': False,
        }

    @api.model
    def _join_text_parts(self, *parts):
        return ' '.join(part for part in parts if part)

    @api.model
    def _counter_from_mapping(self, texts, mapping, fallback=False):
        counter = Counter()
        for text in texts:
            normalized = _normalize_text(text)
            if not normalized:
                continue
            matched = False
            for label, keywords in mapping.items():
                if any(keyword in normalized for keyword in keywords):
                    counter[label] += 1
                    matched = True
            if fallback and not matched:
                counter[fallback] += 1
        return counter

    @api.model
    def _word_counter(self, texts):
        counter = Counter()
        for text in texts:
            normalized = _normalize_text(text)
            for token in re.findall(r'[a-z0-9]+', normalized):
                if len(token) < 3 or token in STOPWORDS or token.isdigit():
                    continue
                counter[token] += 1
        return counter

    @api.model
    def _phrase_counter(self, texts):
        counter = Counter()
        for text in texts:
            normalized = _normalize_text(text)
            for phrase, label in NEGATIVE_PHRASES.items():
                if phrase in normalized:
                    counter['%s (%s)' % (phrase, label)] += 1
        return counter

    @api.model
    def _ngram_counter(self, texts, size):
        counter = Counter()
        for text in texts:
            tokens = [
                token for token in re.findall(r'[a-z0-9]+', _normalize_text(text))
                if len(token) >= 3 and token not in STOPWORDS and not token.isdigit()
            ]
            for index in range(len(tokens) - size + 1):
                gram = ' '.join(tokens[index:index + size])
                counter[gram] += 1
        return counter

    @api.model
    def _room_area_counter(self, records):
        counter = Counter()
        for record in records:
            text = self._join_text_parts(record.complaints_text, record.requests_text, record.original_text)
            if record.room_number:
                counter['Oda %s' % record.room_number] += 1
            normalized = _normalize_text(text)
            for area, keywords in AREA_KEYWORDS.items():
                if any(keyword in normalized for keyword in keywords):
                    counter[area] += 1
        return counter

    @api.model
    def _format_counter_lines(self, counter, limit=10):
        if not counter:
            return 'Veri bulunamadi.'
        return '\n'.join('%s: %s' % (label, count) for label, count in counter.most_common(limit))

    @api.model
    def _format_like_counter_lines(self, counter, limit=10):
        if not counter:
            return 'Veri bulunamadi.'
        return '\n'.join(
            '%s: %s begeni kaydinda gecti' % (label, count)
            for label, count in counter.most_common(limit)
        )

    @api.model
    def _format_word_analysis(self, word_counter, bigram_counter, trigram_counter):
        sections = []
        if word_counter:
            sections.append('Tekil Kelimeler:\n%s' % self._format_counter_lines(word_counter, limit=20))
        if bigram_counter:
            sections.append('Ikili Kelime Gruplari:\n%s' % self._format_counter_lines(bigram_counter, limit=15))
        if trigram_counter:
            sections.append('Uclu Kelime Gruplari:\n%s' % self._format_counter_lines(trigram_counter, limit=10))
        return '\n\n'.join(sections) if sections else 'Veri bulunamadi.'

    @api.model
    def _format_percentage_lines(self, counter):
        if not counter:
            return 'Veri bulunamadi.'
        total = sum(counter.values()) or 1
        return '\n'.join(
            '%s: %s adet (%%%s)' % (label, count, round((count / total) * 100, 2))
            for label, count in counter.most_common()
        )

    @api.model
    def _build_python_summary_html(
        self,
        top_complaint_topics_text,
        department_distribution_text,
        top_likes_text,
        top_rooms_areas_text,
    ):
        sections = [
            ('En Cok Sikayet Edilen Konular', top_complaint_topics_text),
            ('Departman Bazli Dagilim', department_distribution_text),
            ('En Cok Beğenilen Konular', top_likes_text),
            ('En Cok Ariza Alinan Oda/Mekanlar', top_rooms_areas_text),
        ]
        return ''.join('<h4>%s</h4><pre>%s</pre>' % (title, body) for title, body in sections)

    @api.model
    def _read_xlsx_rows(self, binary_content):
        with zipfile.ZipFile(io.BytesIO(binary_content)) as archive:
            shared_strings = self._read_shared_strings(archive)
            style_map = self._read_style_map(archive)
            sheet_path = self._get_first_sheet_path(archive)
            root = ET.fromstring(archive.read(sheet_path))
        rows = root.findall('.//main:sheetData/main:row', XLSX_NS)
        if not rows:
            raise ValidationError('Excel icinde satir bulunamadi.')
        header_index, headers, field_names = self._find_header_row(rows, shared_strings, style_map)
        matched_fields = [field_name for field_name in field_names if field_name]
        result = []
        for row in rows[header_index + 1:]:
            values = self._extract_row_values(row, shared_strings, style_map)
            row_vals = {}
            for index, field_name in enumerate(field_names):
                if not field_name:
                    continue
                row_vals[field_name] = values[index] if index < len(values) else False
            if any(row_vals.values()):
                result.append(row_vals)
        return {
            'headers': headers,
            'matched_fields': matched_fields,
            'rows': result,
        }

    @api.model
    def _find_header_row(self, rows, shared_strings, style_map):
        best_index = 0
        best_headers = self._extract_row_values(rows[0], shared_strings, style_map)
        best_field_names = [HEADER_ALIASES.get(_normalize_header(header or '')) for header in best_headers]
        best_score = len([field_name for field_name in best_field_names if field_name])
        for index, row in enumerate(rows[:10]):
            headers = self._extract_row_values(row, shared_strings, style_map)
            field_names = [HEADER_ALIASES.get(_normalize_header(header or '')) for header in headers]
            score = len([field_name for field_name in field_names if field_name])
            if score > best_score:
                best_index = index
                best_headers = headers
                best_field_names = field_names
                best_score = score
        return best_index, best_headers, best_field_names

    @api.model
    def _get_first_sheet_path(self, archive):
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        first_sheet = workbook.find('.//main:sheets/main:sheet', XLSX_NS)
        if first_sheet is None:
            raise ValidationError('Excel sayfasi bulunamadi.')
        rel_id = first_sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        for rel in rels.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            if rel.attrib.get('Id') == rel_id:
                return 'xl/%s' % rel.attrib.get('Target')
        raise ValidationError('Excel sayfa iliskisi bulunamadi.')

    @api.model
    def _read_shared_strings(self, archive):
        if 'xl/sharedStrings.xml' not in archive.namelist():
            return []
        root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        values = []
        for item in root.findall('.//main:si', XLSX_NS):
            values.append(''.join(node.text or '' for node in item.findall('.//main:t', XLSX_NS)))
        return values

    @api.model
    def _read_style_map(self, archive):
        if 'xl/styles.xml' not in archive.namelist():
            return {}
        root = ET.fromstring(archive.read('xl/styles.xml'))
        custom_numfmts = {
            int(node.attrib['numFmtId']): (node.attrib.get('formatCode') or '').lower()
            for node in root.findall('.//main:numFmts/main:numFmt', XLSX_NS)
            if node.attrib.get('numFmtId')
        }
        style_map = {}
        for index, xf in enumerate(root.findall('.//main:cellXfs/main:xf', XLSX_NS)):
            num_fmt_id = int(xf.attrib.get('numFmtId', 0))
            format_code = custom_numfmts.get(num_fmt_id, '')
            style_map[index] = {
                'is_date': num_fmt_id in DEFAULT_DATE_NUMFMTS or any(token in format_code for token in ('yy', 'dd', 'mm', 'h', 'ss')),
                'format_code': format_code,
            }
        return style_map

    @api.model
    def _extract_row_values(self, row, shared_strings, style_map):
        values_by_index = {}
        max_index = -1
        for cell in row.findall('main:c', XLSX_NS):
            index = self._column_index_from_ref(cell.attrib.get('r', ''))
            max_index = max(max_index, index)
            values_by_index[index] = self._extract_cell_value(cell, shared_strings, style_map)
        return [values_by_index.get(index, False) for index in range(max_index + 1)]

    @api.model
    def _extract_cell_value(self, cell, shared_strings, style_map):
        cell_type = cell.attrib.get('t')
        style_id = int(cell.attrib.get('s', 0))
        value_node = cell.find('main:v', XLSX_NS)
        inline_node = cell.find('main:is/main:t', XLSX_NS)
        raw_value = value_node.text if value_node is not None else (inline_node.text if inline_node is not None else '')
        if raw_value in (None, ''):
            return False
        if cell_type == 's':
            index = int(raw_value)
            return shared_strings[index] if index < len(shared_strings) else False
        if cell_type == 'inlineStr':
            return raw_value
        if cell_type == 'b':
            return 'EVET' if raw_value == '1' else 'HAYIR'
        style = style_map.get(style_id, {})
        if style.get('is_date'):
            return self._convert_excel_date(raw_value, style.get('format_code', ''))
        if self._looks_numeric(raw_value):
            return self._format_numeric(raw_value)
        return raw_value.strip()

    @api.model
    def _convert_excel_date(self, raw_value, format_code):
        number = float(raw_value)
        converted = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=number)
        if any(token in format_code for token in ('h', 'ss')) or converted.time() != datetime.time(0, 0):
            return converted.strftime('%H:%M')
        return converted.date()

    @api.model
    def _format_numeric(self, raw_value):
        number = float(raw_value)
        return str(int(number)) if number.is_integer() else str(number)

    @api.model
    def _looks_numeric(self, raw_value):
        try:
            float(raw_value)
            return True
        except (TypeError, ValueError):
            return False

    @api.model
    def _column_index_from_ref(self, ref):
        letters = ''.join(char for char in ref if char.isalpha())
        index = 0
        for char in letters:
            index = index * 26 + (ord(char.upper()) - 64)
        return max(index - 1, 0)

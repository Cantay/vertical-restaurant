import re
import unicodedata
from datetime import datetime, time

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError


TURKISH_CHAR_MAP = str.maketrans({
    'ı': 'i',
    'İ': 'I',
    'ğ': 'g',
    'Ğ': 'G',
    'ü': 'u',
    'Ü': 'U',
    'ş': 's',
    'Ş': 'S',
    'ö': 'o',
    'Ö': 'O',
    'ç': 'c',
    'Ç': 'C',
})


def _slugify(value):
    value = (value or '').translate(TURKISH_CHAR_MAP)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()
    return value or 'form'


def _split_option_tokens(value):
    tokens = []
    for chunk in re.split(r'[\n,;]+', value or ''):
        chunk = chunk.strip()
        if chunk:
            tokens.append(chunk)
    return tokens


def _format_date_display(value):
    if not value:
        return False
    if isinstance(value, str):
        value = fields.Date.to_date(value)
    return value.strftime('%d/%m/%Y') if value else False


def _format_datetime_display(value):
    if not value:
        return False
    if isinstance(value, str):
        value = fields.Datetime.to_datetime(value)
    return value.strftime('%d/%m/%Y %H:%M:%S') if value else False


class RonixOnlineFormTemplate(models.Model):
    _name = 'ronix.online.form.template'
    _description = 'Ronix Cevrimici Form Sablonu'
    _order = 'sequence asc, name asc, id desc'

    STATE_SELECTION = [
        ('draft', 'Taslak'),
        ('published', 'Yayinda'),
        ('archived', 'Arsivde'),
    ]

    name = fields.Char(string='Form Adi', required=True)
    slug = fields.Char(string='Kisa URL', required=True, index=True, copy=False)
    sequence = fields.Integer(string='Sira', default=10)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        required=True,
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    description = fields.Text(string='Aciklama')
    calendar_color = fields.Char(
        string='Takvim Rengi',
        default='#b98a45',
        help='Takvimde bu forma ait kayitlar bu renkle gosterilir.',
    )
    calendar_field_id = fields.Many2one(
        'ronix.online.form.field',
        string='Takvimde Kullanilacak Tarih Alani',
        domain="[('template_id', '=', id), ('field_type', 'in', ['date', 'datetime'])]",
        help='Takvim kaydinin hangi tarih alanina gore yerlestirilecegini secin.',
    )
    thank_you_message = fields.Text(
        string='Basari Mesaji',
        default='Formunuz basariyla kaydedildi.',
    )
    submit_button_label = fields.Char(string='Gonder Butonu Yazisi', default='Gonder')
    state = fields.Selection(STATE_SELECTION, string='Durum', default='draft', required=True, index=True)
    field_ids = fields.One2many(
        'ronix.online.form.field',
        'template_id',
        string='Alanlar',
        copy=True,
    )
    submission_ids = fields.One2many(
        'ronix.online.form.submission',
        'template_id',
        string='Gonderimler',
    )
    submission_count = fields.Integer(string='Gonderim Sayisi', compute='_compute_submission_count')
    frontend_path = fields.Char(string='Form Linki', compute='_compute_frontend_path')
    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('ronix_online_form_template_location_slug_unique', 'unique(location_id, slug)', 'Bu lokasyonda ayni kisa URL ile baska bir form zaten var.'),
    ]

    @api.depends('submission_ids')
    def _compute_submission_count(self):
        for record in self:
            record.submission_count = len(record.submission_ids)

    @api.depends('slug', 'location_id.token')
    def _compute_frontend_path(self):
        for record in self:
            if record.slug and record.location_id.token:
                record.frontend_path = '/online-forms/%s/%s' % (record.location_id.token, record.slug)
            else:
                record.frontend_path = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['slug'] = self._prepare_unique_slug(vals.get('slug') or vals.get('name'))
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if 'slug' in vals:
            for record in self:
                vals['slug'] = record._prepare_unique_slug(
                    vals.get('slug'),
                    exclude_id=record.id,
                    location_id=vals.get('location_id') or record.location_id.id,
                )
                break
        return super().write(vals)

    def _prepare_unique_slug(self, source, exclude_id=None, location_id=None):
        base_slug = _slugify(source)
        location_id = location_id or self.location_id.id
        slug = base_slug
        counter = 2
        domain = [('slug', '=', slug)]
        if location_id:
            domain.append(('location_id', '=', location_id))
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        while self.search_count(domain):
            slug = '%s-%s' % (base_slug, counter)
            counter += 1
            domain = [('slug', '=', slug)]
            if location_id:
                domain.append(('location_id', '=', location_id))
            if exclude_id:
                domain.append(('id', '!=', exclude_id))
        return slug

    @api.constrains('slug')
    def _check_slug(self):
        for record in self:
            if record.slug != _slugify(record.slug):
                raise ValidationError('Slug sadece kucuk harf, rakam ve tire icerebilir.')

    def action_publish(self):
        self.write({'state': 'published'})
        return True

    def action_set_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_archive_template(self):
        self.write({'state': 'archived'})
        return True

    def action_open_frontend(self):
        self.ensure_one()
        if not self.frontend_path:
            raise ValidationError('Frontend URL olusturulamadi.')
        return {
            'type': 'ir.actions.act_url',
            'url': self.frontend_path,
            'target': 'new',
        }

    def action_view_submissions(self):
        self.ensure_one()
        action = self.env.ref('ronix_online_form_manager.action_ronix_online_form_submission').read()[0]
        action['domain'] = [('template_id', '=', self.id)]
        action['context'] = {'default_template_id': self.id}
        return action

    def get_frontend_fields(self):
        self.ensure_one()
        return self.field_ids.sorted(key=lambda field: (field.sequence, field.id))

    def can_edit_frontend(self, user=None):
        self.ensure_one()
        user = user or self.env.user
        if not user or user._is_public():
            return False
        if user.has_group('base.group_system'):
            return True
        if user.has_group('ronix_online_form_manager.group_ronix_online_form_admin'):
            return True
        if user.id in self.location_id.manager_ids.ids:
            return True
        return False

    def apply_frontend_layout(self, layout_items):
        self.ensure_one()
        if not self.can_edit_frontend():
            raise AccessError('Bu formu duzenleme yetkiniz bulunmuyor.')
        if not isinstance(layout_items, list):
            raise ValidationError('Gecersiz layout verisi.')

        field_map = {field.id: field for field in self.field_ids}
        seen_ids = set()
        sequence = 10
        for item in layout_items:
            if not isinstance(item, dict):
                continue
            field_id = int(item.get('field_id') or 0)
            field_record = field_map.get(field_id)
            if not field_record or field_id in seen_ids:
                continue
            values = {'sequence': sequence}
            if field_record.field_type != 'section':
                span = str(item.get('column_span') or field_record.column_span or '6')
                values['column_span'] = span if span in {'6', '12'} else '6'
            field_record.write(values)
            seen_ids.add(field_id)
            sequence += 10

        for field_record in self.field_ids.sorted(key=lambda field: (field.sequence, field.id)):
            if field_record.id in seen_ids:
                continue
            values = {'sequence': sequence}
            if field_record.field_type != 'section' and field_record.column_span not in {'6', '12'}:
                values['column_span'] = '6'
            field_record.write(values)
            sequence += 10

    def build_submission_from_post(self, post):
        self.ensure_one()
        errors = {}
        value_commands = []
        payload = {}
        for field in self.get_frontend_fields():
            if field.field_type == 'section':
                continue
            parsed = field.parse_post_value(post.get(field.code))
            if field.required and not parsed['has_value']:
                errors[field.code] = 'Bu alan zorunludur.'
                continue
            if parsed['error']:
                errors[field.code] = parsed['error']
                continue
            payload[field.code] = parsed['payload_value']
            value_commands.append(fields.Command.create({
                'field_id': field.id,
                'field_name': field.name,
                'field_code': field.code,
                'field_type': field.field_type,
                'value_text': parsed['value_text'],
                'value_integer': parsed['value_integer'],
                'value_float': parsed['value_float'],
                'value_date': parsed['value_date'],
                'value_datetime': parsed['value_datetime'],
                'value_boolean': parsed['value_boolean'],
            }))
        if errors:
            return {'errors': errors, 'payload': payload, 'value_commands': []}
        return {'errors': {}, 'payload': payload, 'value_commands': value_commands}


class RonixOnlineFormField(models.Model):
    _name = 'ronix.online.form.field'
    _description = 'Ronix Cevrimici Form Alani'
    _order = 'sequence asc, id asc'

    FIELD_TYPE_SELECTION = [
        ('section', 'Bolum basligi'),
        ('char', 'Kisa metin'),
        ('text', 'Uzun metin / aciklama'),
        ('email', 'E-posta adresi'),
        ('phone', 'Telefon numarasi'),
        ('integer', 'Tam sayi (1, 2, 3 gibi)'),
        ('float', 'Ondalikli sayi (0.1 gibi)'),
        ('date', 'Tarih'),
        ('datetime', 'Tarih ve saat'),
        ('boolean', 'Onay kutusu (evet/hayir)'),
        ('selection', 'Secim listesi'),
    ]
    COLUMN_SPAN_SELECTION = [
        ('6', 'Yarim genislik'),
        ('12', 'Tam genislik'),
    ]

    template_id = fields.Many2one(
        'ronix.online.form.template',
        string='Form',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(string='Sira', default=10)
    name = fields.Char(string='Alan Etiketi', required=True)
    code = fields.Char(string='Teknik Anahtar')
    field_type = fields.Selection(FIELD_TYPE_SELECTION, string='Alan Tipi', required=True, default='char')
    required = fields.Boolean(string='Zorunlu', default=False)
    placeholder = fields.Char(string='Ornek Metin')
    help_text = fields.Char(string='Yardim Metni')
    selection_options_text = fields.Text(
        string='Secenekler',
        help='Secenekleri virgulle, noktali virgulle veya alt alta yazabilirsiniz. Isterseniz kod|etiket formatini da kullanabilirsiniz.',
    )
    column_span = fields.Selection(COLUMN_SPAN_SELECTION, string='Alan Genisligi', default='6', required=True)
    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('ronix_online_form_field_template_code_unique', 'unique(template_id, code)', 'Teknik anahtar her form icinde benzersiz olmalidir.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code'] = self._prepare_code(vals.get('code') or vals.get('name'))
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if 'code' in vals:
            vals['code'] = self._prepare_code(vals.get('code'))
        elif 'name' in vals:
            for record in self:
                if record.code == record._prepare_code(record.name):
                    vals['code'] = record._prepare_code(vals.get('name'))
                break
        return super().write(vals)

    @api.onchange('name')
    def _onchange_name_set_code(self):
        for record in self:
            generated_from_current_name = record._prepare_code(record.name)
            generated_from_origin_name = record._prepare_code(record._origin.name)
            if not record.code or record.code == generated_from_origin_name:
                record.code = generated_from_current_name

    @api.onchange('code')
    def _onchange_code_normalize(self):
        for record in self:
            if record.code:
                record.code = record._prepare_code(record.code)

    @api.constrains('field_type', 'selection_options_text')
    def _check_field_configuration(self):
        for record in self:
            if not record.code:
                raise ValidationError('Teknik anahtar otomatik olusmadi. Lutfen bir alan etiketi veya teknik anahtar girin.')
            if record.field_type == 'selection' and not record.get_selection_options():
                raise ValidationError('Secim listesi alanlari icin "Secenekler" kutusuna en az bir secenek yazin.')

    def _prepare_code(self, source):
        code = _slugify(source).replace('-', '_')
        return code or 'field'

    def get_selection_options(self):
        self.ensure_one()
        options = []
        for line in _split_option_tokens(self.selection_options_text):
            if not line:
                continue
            if '|' in line:
                key, label = line.split('|', 1)
                key = self._prepare_code(key)
                label = label.strip()
            else:
                label = line
                key = self._prepare_code(line)
            options.append((key, label or key))
        return options

    def parse_post_value(self, raw_value):
        self.ensure_one()
        raw_text = (raw_value or '').strip() if isinstance(raw_value, str) else raw_value
        result = {
            'error': False,
            'has_value': False,
            'payload_value': False,
            'value_text': False,
            'value_integer': False,
            'value_float': False,
            'value_date': False,
            'value_datetime': False,
            'value_boolean': False,
        }
        if self.field_type == 'boolean':
            value = raw_text in ('on', 'true', '1', 'yes', 'y')
            result.update({
                'has_value': value,
                'payload_value': value,
                'value_text': 'Evet' if value else 'Hayir',
                'value_boolean': value,
            })
            return result
        if raw_text in (False, None, ''):
            return result

        if self.field_type in ('char', 'text', 'email', 'phone'):
            result.update({
                'has_value': True,
                'payload_value': raw_text,
                'value_text': raw_text,
            })
            return result
        if self.field_type == 'integer':
            try:
                integer_value = int(float(str(raw_text).replace(',', '.')))
            except (TypeError, ValueError):
                result['error'] = 'Gecerli bir tam sayi girin.'
                return result
            result.update({
                'has_value': True,
                'payload_value': integer_value,
                'value_text': str(integer_value),
                'value_integer': integer_value,
            })
            return result
        if self.field_type == 'float':
            try:
                float_value = float(str(raw_text).replace(',', '.'))
            except (TypeError, ValueError):
                result['error'] = 'Gecerli bir sayi girin.'
                return result
            result.update({
                'has_value': True,
                'payload_value': float_value,
                'value_text': str(float_value),
                'value_float': float_value,
            })
            return result
        if self.field_type == 'date':
            try:
                date_value = fields.Date.to_date(raw_text)
            except (TypeError, ValueError):
                date_value = False
            if not date_value:
                result['error'] = 'Gecerli bir tarih girin.'
                return result
            result.update({
                'has_value': True,
                'payload_value': fields.Date.to_string(date_value),
                'value_text': _format_date_display(date_value),
                'value_date': date_value,
            })
            return result
        if self.field_type == 'datetime':
            try:
                datetime_value = fields.Datetime.to_datetime(raw_text)
            except (TypeError, ValueError):
                datetime_value = False
            if not datetime_value:
                result['error'] = 'Gecerli bir tarih-saat girin.'
                return result
            result.update({
                'has_value': True,
                'payload_value': fields.Datetime.to_string(datetime_value),
                'value_text': _format_datetime_display(datetime_value),
                'value_datetime': datetime_value,
            })
            return result
        if self.field_type == 'selection':
            options = dict(self.get_selection_options())
            if raw_text not in options:
                result['error'] = 'Gecerli bir secenek secin.'
                return result
            result.update({
                'has_value': True,
                'payload_value': raw_text,
                'value_text': options[raw_text],
            })
            return result
        return result


class RonixOnlineFormSubmission(models.Model):
    _name = 'ronix.online.form.submission'
    _description = 'Ronix Cevrimici Form Gonderimi'
    _order = 'submitted_on desc, id desc'

    STATE_SELECTION = [
        ('new', 'Yeni'),
        ('reviewed', 'Incelendi'),
        ('archived', 'Arsivlendi'),
    ]

    name = fields.Char(string='Kayit Adi', compute='_compute_name', store=True)
    template_id = fields.Many2one(
        'ronix.online.form.template',
        string='Form',
        required=True,
        ondelete='restrict',
        index=True,
    )
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        related='template_id.location_id',
        store=True,
        index=True,
    )
    submitted_on = fields.Datetime(string='Gonderim Tarihi', default=fields.Datetime.now, required=True, index=True)
    calendar_color = fields.Char(
        string='Takvim Rengi',
        related='template_id.calendar_color',
        store=True,
    )
    calendar_date = fields.Datetime(
        string='Takvim Tarihi',
        compute='_compute_calendar_date',
        store=True,
        index=True,
    )
    calendar_date_display = fields.Char(
        string='Takvim Tarihi',
        compute='_compute_calendar_date',
    )
    state = fields.Selection(STATE_SELECTION, string='Durum', default='new', required=True)
    value_ids = fields.One2many(
        'ronix.online.form.submission.value',
        'submission_id',
        string='Alan Degerleri',
        copy=False,
    )
    payload_json = fields.Text(string='Ham JSON Verisi', readonly=True)
    note = fields.Text(string='Not')

    @api.depends('template_id', 'submitted_on')
    def _compute_name(self):
        for record in self:
            timestamp = _format_datetime_display(record.submitted_on) if record.submitted_on else 'Yeni'
            record.name = '%s - %s' % (record.template_id.name or 'Form', timestamp)

    @api.depends(
        'template_id.calendar_field_id',
        'value_ids.field_id',
        'value_ids.value_date',
        'value_ids.value_datetime',
    )
    def _compute_calendar_date(self):
        for record in self:
            calendar_datetime = False
            calendar_display = False
            reference_field = record.template_id.calendar_field_id
            if reference_field:
                matching_value = record.value_ids.filtered(lambda value: value.field_id == reference_field)[:1]
                if matching_value:
                    if reference_field.field_type == 'date' and matching_value.value_date:
                        calendar_datetime = datetime.combine(matching_value.value_date, time.min)
                        calendar_display = _format_date_display(matching_value.value_date)
                    elif reference_field.field_type == 'datetime' and matching_value.value_datetime:
                        calendar_datetime = matching_value.value_datetime
                        calendar_display = _format_datetime_display(matching_value.value_datetime)
            record.calendar_date = calendar_datetime
            record.calendar_date_display = calendar_display

    @api.constrains('calendar_color')
    def _check_calendar_color(self):
        color_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
        for record in self:
            if record.calendar_color and not color_pattern.match(record.calendar_color):
                raise ValidationError('Takvim rengi gecersiz. Ornek format: #b98a45')

    def action_mark_reviewed(self):
        self.write({'state': 'reviewed'})
        return True

    def action_archive_submission(self):
        self.write({'state': 'archived'})
        return True

    def action_print_pdf(self):
        return self.env.ref('ronix_online_form_manager.action_report_online_form_submission').report_action(self)

    def _get_report_groups(self):
        groups = []
        for template in self.mapped('template_id'):
            template_submissions = self.filtered(lambda submission: submission.template_id == template)
            fields_to_print = template.get_frontend_fields().filtered(lambda field: field.field_type != 'section')
            rows = []
            for submission in template_submissions.sorted(lambda record: (record.calendar_date or record.submitted_on or fields.Datetime.now(), record.id)):
                values_by_field_id = {value.field_id.id: value.display_value or '' for value in submission.value_ids if value.field_id}
                rows.append({
                    'submission': submission,
                    'values': [values_by_field_id.get(field.id, '') for field in fields_to_print],
                })
            groups.append({
                'template': template,
                'fields': fields_to_print,
                'rows': rows,
            })
        return groups


class RonixOnlineFormSubmissionValue(models.Model):
    _name = 'ronix.online.form.submission.value'
    _description = 'Ronix Cevrimici Form Alan Degeri'
    _order = 'id asc'

    submission_id = fields.Many2one(
        'ronix.online.form.submission',
        string='Gonderim',
        required=True,
        ondelete='cascade',
        index=True,
    )
    field_id = fields.Many2one(
        'ronix.online.form.field',
        string='Alan',
        ondelete='set null',
        index=True,
    )
    field_name = fields.Char(string='Alan Etiketi', required=True)
    field_code = fields.Char(string='Teknik Anahtar', required=True)
    field_type = fields.Selection(RonixOnlineFormField.FIELD_TYPE_SELECTION, string='Alan Tipi', required=True)
    value_text = fields.Text(string='Metin Degeri')
    value_integer = fields.Integer(string='Tam Sayi Degeri')
    value_float = fields.Float(string='Ondalikli Sayi Degeri', digits=(16, 2))
    value_date = fields.Date(string='Tarih Degeri')
    value_datetime = fields.Datetime(string='Tarih Saat Degeri')
    value_boolean = fields.Boolean(string='Onay Durumu')
    display_value = fields.Char(string='Gorunen Deger', compute='_compute_display_value')

    @api.depends(
        'field_type',
        'value_text',
        'value_integer',
        'value_float',
        'value_date',
        'value_datetime',
        'value_boolean',
    )
    def _compute_display_value(self):
        for record in self:
            display_value = record.value_text or False
            if record.field_type == 'date':
                display_value = _format_date_display(record.value_date)
            elif record.field_type == 'datetime':
                display_value = _format_datetime_display(record.value_datetime)
            elif record.field_type == 'integer':
                display_value = str(record.value_integer) if record.value_integer not in (False, None) else False
            elif record.field_type == 'float':
                display_value = str(record.value_float) if record.value_float not in (False, None) else False
            elif record.field_type == 'boolean':
                display_value = 'Evet' if record.value_boolean else 'Hayir'
            record.display_value = display_value

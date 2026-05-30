import base64

from odoo import api, fields, models
from odoo.tools.image import image_process
from dateutil.relativedelta import relativedelta


MOJIBAKE_MARKERS = ('Ã', 'Ä', 'Å', 'Ð', 'Þ', '�')
MOJIBAKE_REPLACEMENTS = {
    'Ã§': 'ç',
    'Ã‡': 'Ç',
    'Ã¶': 'ö',
    'Ã–': 'Ö',
    'Ã¼': 'ü',
    'Ãœ': 'Ü',
    'Ä±': 'ı',
    'Ä°': 'İ',
    'ÅŸ': 'ş',
    'Åž': 'Ş',
    'ÄŸ': 'ğ',
    'Äž': 'Ğ',
}


class RonixQualityOperationalNonconformity(models.Model):
    _name = 'ronix.quality.operational.nonconformity'
    _description = 'Ronix Quality Operational Nonconformity'
    _order = 'nonconformity_date desc, id desc'
    _rec_name = 'department_name'

    nonconformity_description = fields.Text(string='Uygunsuzluk Açıklaması', required=True)
    nonconformity_date = fields.Date(
        string='Uygunsuzluk Tarihi',
        required=True,
        default=fields.Date.context_today,
    )
    photo = fields.Image(string='Fotoğraf', max_width=1280, max_height=1280)
    nonconformity_description_short = fields.Char(
        string='Açıklama Özeti',
        compute='_compute_nonconformity_description_short',
    )
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    department_id = fields.Many2one(
        'ronix.quality.inspection.department',
        string='Departman',
        ondelete='set null',
        index=True,
    )
    department_name = fields.Char(string='Departman', required=True, index=True)
    deadline_date = fields.Date(string='Termin Tarihi')
    state = fields.Selection(
        [
            ('new_job', 'Yeni İş'),
            ('ongoing', 'Devam Ediyor'),
            ('ordered', 'Siparişte'),
            ('done', 'Tamamlandı'),
        ],
        string='Son Durumu',
        required=True,
        default='new_job',
    )
    active = fields.Boolean(default=True)

    def init(self):
        self.env.cr.execute("""
            UPDATE ronix_quality_operational_nonconformity
               SET state = 'ordered'
             WHERE state = 'infrastructure'
        """)
        self.env.cr.execute("""
            UPDATE ronix_quality_operational_nonconformity AS nonconformity
               SET department_id = department.id
              FROM ronix_quality_inspection_department AS department
             WHERE nonconformity.department_id IS NULL
               AND nonconformity.location_id = department.location_id
               AND TRIM(COALESCE(nonconformity.department_name, '')) = TRIM(department.name)
        """)

    @api.depends('nonconformity_description')
    def _compute_nonconformity_description_short(self):
        for record in self:
            description = record._repair_mojibake_text(record.nonconformity_description or '').strip()
            record.nonconformity_description_short = (
                description[:77].rstrip() + '...'
                if len(description) > 80
                else description
            )

    @api.onchange('department_id')
    def _onchange_department_id(self):
        for record in self:
            if record.department_id:
                record.department_name = record._repair_mojibake_text(record.department_id.name or '')

    @api.onchange('nonconformity_date')
    def _onchange_nonconformity_date(self):
        for record in self:
            if record.nonconformity_date:
                record.deadline_date = record.nonconformity_date + relativedelta(months=1)

    @api.model
    def _get_public_report_domain(self, date_from=None, date_to=None, department_id=None, department_name=None, state=None):
        domain = [('active', '=', True)]
        if date_from:
            domain.append(('nonconformity_date', '>=', date_from))
        if date_to:
            domain.append(('nonconformity_date', '<=', date_to))
        department = self.env['ronix.quality.inspection.department'].browse(department_id).exists() if department_id else False
        if department:
            repaired_name = self._repair_mojibake_text(department.name or '')
            domain.extend(['|', ('department_id', '=', department.id), ('department_name', '=', repaired_name)])
        if department_name:
            domain.append(('department_name', '=', self._repair_mojibake_text(department_name)))
        if state in dict(self._fields['state'].selection):
            domain.append(('state', '=', state))
        return domain

    @api.model
    def _get_public_report_records(self, date_from=None, date_to=None, department_id=None, department_name=None, state=None):
        domain = self._get_public_report_domain(
            date_from=date_from,
            date_to=date_to,
            department_id=department_id,
            department_name=department_name,
            state=state,
        )
        return self.search(domain, order='department_name asc, nonconformity_date desc, id desc')

    @api.model
    def _get_public_report_departments(self):
        records = self.search([('active', '=', True)], order='department_name asc, id asc')
        departments = []
        seen = set()
        for record in records:
            department = self._repair_mojibake_text(record.department_name or '').strip()
            if department and department not in seen:
                seen.add(department)
                departments.append(department)
        return departments

    @api.model
    def _get_filter_departments(self):
        return self.env['ronix.quality.inspection.department'].search(
            [('active', '=', True)],
            order='sequence asc, name asc, id asc',
        )

    @api.model_create_multi
    def create(self, vals_list):
        sanitized_vals_list = [self._prepare_vals(vals) for vals in vals_list]
        return super().create(sanitized_vals_list)

    def write(self, vals):
        prepared_vals = self._prepare_vals(vals, record=self)
        return super().write(prepared_vals)

    @api.model
    def _repair_mojibake_text(self, value):
        if not isinstance(value, str) or not any(marker in value for marker in MOJIBAKE_MARKERS):
            return value

        repaired = value
        for source_encoding in ('latin1', 'cp1254', 'iso8859_9'):
            try:
                candidate = repaired.encode(source_encoding).decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if candidate != repaired:
                repaired = candidate

        for wrong, correct in MOJIBAKE_REPLACEMENTS.items():
            repaired = repaired.replace(wrong, correct)

        return repaired

    @api.model
    def _sanitize_text_values(self, vals):
        sanitized_vals = dict(vals)
        for field_name in ('nonconformity_description', 'department_name'):
            if field_name in sanitized_vals:
                sanitized_vals[field_name] = self._repair_mojibake_text(sanitized_vals[field_name])
        if sanitized_vals.get('photo'):
            sanitized_vals['photo'] = self._compress_photo(sanitized_vals['photo'])
        return sanitized_vals

    @api.model
    def _prepare_vals(self, vals, record=None):
        prepared_vals = self._sanitize_text_values(vals)
        department_id = prepared_vals.get('department_id')
        if department_id:
            department = self.env['ronix.quality.inspection.department'].browse(department_id).exists()
            if department:
                prepared_vals['department_name'] = self._repair_mojibake_text(department.name or '')
        if not prepared_vals.get('deadline_date') and prepared_vals.get('nonconformity_date'):
            base_date = fields.Date.to_date(prepared_vals['nonconformity_date'])
            prepared_vals['deadline_date'] = fields.Date.to_string(base_date + relativedelta(months=1))
        if record and not prepared_vals.get('department_name') and 'department_id' not in prepared_vals:
            return prepared_vals
        return prepared_vals

    @api.model
    def _compress_photo(self, photo):
        try:
            photo_bytes = base64.b64decode(photo)
        except Exception:
            return photo
        processed = image_process(
            photo_bytes,
            size=(1280, 1280),
            quality=55,
            output_format='JPEG',
        )
        return base64.b64encode(processed) if processed else photo

    def get_report_description(self):
        self.ensure_one()
        return self._repair_mojibake_text(self.nonconformity_description)

    def get_report_department_name(self):
        self.ensure_one()
        return self._repair_mojibake_text(self.department_name)

    def get_report_state_label(self):
        self.ensure_one()
        label = dict(self._fields['state'].selection).get(self.state, '')
        return self._repair_mojibake_text(label)

    def get_report_photo(self):
        self.ensure_one()
        if not self.photo:
            return False
        return self._compress_photo(self.photo)

    @api.model
    def format_report_date(self, value):
        if not value:
            return '-'
        return fields.Date.to_date(value).strftime('%d/%m/%Y')

    def _get_state_label_class(self):
        self.ensure_one()
        mapping = {
            'new_job': 'bg-secondary text-white',
            'ongoing': 'bg-warning text-dark',
            'ordered': 'bg-info text-white',
            'done': 'bg-success text-white',
        }
        return mapping.get(self.state, 'bg-secondary text-white')

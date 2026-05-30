import json

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class RonixQualityGoodsAcceptanceForm(models.Model):
    _name = 'ronix.quality.goods.acceptance.form'
    _description = 'Ronix Quality Goods Acceptance Form'
    _order = 'create_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    operator_name = fields.Char(string='Islemi Yapan', default=lambda self: self.env.user.name)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    line_ids = fields.One2many(
        'ronix.quality.goods.acceptance.form.line',
        'form_id',
        string='Satirlar',
    )
    first_line_date = fields.Date(string='Ilk Tarih', compute='_compute_first_line_date', store=True)
    line_count = fields.Integer(compute='_compute_line_count')
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    active = fields.Boolean(default=True)

    @api.depends('operator_name', 'line_ids.line_date')
    def _compute_name(self):
        for record in self:
            first_date = record.line_ids[:1].line_date
            parts = [fields.Date.to_string(first_date) if first_date else '', record.operator_name or '']
            record.name = ' - '.join(part for part in parts if part) or 'Mal Kabul Formu'

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.depends('line_ids.line_date')
    def _compute_first_line_date(self):
        for record in self:
            record.first_line_date = record.line_ids[:1].line_date or False

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/mal-kabul-formu'

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('ronix_quality_manager.action_report_goods_acceptance_form').report_action(self)


class RonixQualityGoodsAcceptanceFormLine(models.Model):
    _name = 'ronix.quality.goods.acceptance.form.line'
    _description = 'Ronix Quality Goods Acceptance Form Line'
    _order = 'line_date desc, id asc'

    ACCEPTANCE_SELECTION = [
        ('accept', 'Kabul'),
        ('reject', 'Ret'),
        ('conditional', 'Sartli Kabul'),
    ]
    HYGIENE_SELECTION = [
        ('ok', 'Uygun'),
        ('not_ok', 'Uygun Degil'),
    ]

    form_id = fields.Many2one(
        'ronix.quality.goods.acceptance.form',
        string='Form',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    line_date = fields.Date(string='Tarih', required=True, default=fields.Date.context_today)
    product_name_brand = fields.Char(string='Urun (Isim - Marka)')
    batch_no = fields.Char(string='Parti No')
    production_date = fields.Date(string='Uretim Tarihi')
    expiry_date = fields.Date(string='Son Kullanma Tarihi')
    vehicle_hygiene = fields.Selection(HYGIENE_SELECTION, string='Arac Genel Hijyen')
    packaging_hygiene = fields.Selection(HYGIENE_SELECTION, string='Ambalaj Genel Hijyen')
    supplier_name = fields.Char(string='Tedarikci Firma')
    vehicle_temperature = fields.Float(string='Arac Sicaklik', digits=(16, 2))
    product_temperature = fields.Float(string='Urun Sicaklik', digits=(16, 2))
    acceptance_status = fields.Selection(ACCEPTANCE_SELECTION, string='Hammadde Kabul Kriteri')
    description = fields.Char(string='Aciklama')
    expiry_warning = fields.Boolean(compute='_compute_expiry_warning', store=True)
    expiry_warning_label = fields.Char(compute='_compute_expiry_warning')
    skt_checked = fields.Boolean(string='SKT Kontrol Edildi', default=False, copy=False)

    @api.depends('expiry_date')
    def _compute_expiry_warning(self):
        for record in self:
            warning = False
            if record.expiry_date:
                today = fields.Date.context_today(record)
                warning_limit = today + relativedelta(days=7)
                warning = record.expiry_date <= warning_limit
            record.expiry_warning = warning
            record.expiry_warning_label = '⚠' if warning else ''

    def action_mark_skt_checked(self):
        self.write({'skt_checked': True})
        return True

    @api.model
    def parse_frontend_lines(self, payload):
        try:
            rows = json.loads(payload or '[]')
        except json.JSONDecodeError:
            rows = []
        commands = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            values = self._prepare_frontend_line_vals(row)
            if values:
                commands.append(fields.Command.create(values))
        return commands

    @api.model
    def _prepare_frontend_line_vals(self, row):
        values = {
            'line_date': row.get('line_date') or False,
            'product_name_brand': (row.get('product_name_brand') or '').strip(),
            'batch_no': (row.get('batch_no') or '').strip(),
            'production_date': row.get('production_date') or False,
            'expiry_date': row.get('expiry_date') or False,
            'vehicle_hygiene': row.get('vehicle_hygiene') or False,
            'packaging_hygiene': row.get('packaging_hygiene') or False,
            'supplier_name': (row.get('supplier_name') or '').strip(),
            'vehicle_temperature': self._to_float(row.get('vehicle_temperature')),
            'product_temperature': self._to_float(row.get('product_temperature')),
            'acceptance_status': row.get('acceptance_status') or False,
            'description': (row.get('description') or '').strip(),
        }
        if not any(values.get(key) for key in values if key != 'line_date'):
            return False
        if not values['line_date']:
            values['line_date'] = fields.Date.context_today(self)
        return values

    @api.model
    def _to_float(self, value):
        if value in (None, '', False):
            return False
        try:
            return float(str(value).replace(',', '.'))
        except (TypeError, ValueError):
            return False

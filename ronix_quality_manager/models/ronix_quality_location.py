import secrets
import string

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RonixQualityLocation(models.Model):
    _name = 'ronix.quality.location'
    _description = 'Ronix Quality Location'
    _order = 'name asc'

    @api.model
    def _generate_unique_token(self, length=8):
        alphabet = string.ascii_uppercase + string.digits
        for _attempt in range(20):
            token = ''.join(secrets.choice(alphabet) for _index in range(length))
            if not self.search_count([('token', '=', token)]):
                return token
        raise ValidationError('Benzersiz bir lokasyon tokeni olusturulamadi.')

    name = fields.Char(string='Lokasyon Adi', required=True, tracking=True)
    token = fields.Char(
        string='Token',
        required=True,
        copy=False,
        index=True,
        tracking=True,
        default=lambda self: self._generate_unique_token(),
    )
    active = fields.Boolean(default=True)
    manager_ids = fields.Many2many(
        'res.users',
        'ronix_quality_location_res_users_rel',
        'location_id',
        'user_id',
        string='Yoneticiler',
    )
    button_ids = fields.One2many(
        'ronix.quality.button',
        'location_id',
        string='Butonlar',
    )
    button_count = fields.Integer(compute='_compute_button_count')
    
    vapi_enabled = fields.Boolean(default=False, string='Vapi Entegrasyonu')
    vapi_public_key = fields.Char(string='Vapi Public Key')
    vapi_assistant_id = fields.Char(string='Vapi Assistant ID')
    vapi_widget_mode = fields.Selection(
        [
            ('voice', 'Ses'),
            ('chat', 'Sohbet'),
            ('hybrid', 'Hibrit'),
        ],
        string='Vapi Widget Modu',
        default='hybrid',
        required=True,
    )
    vapi_cta_title = fields.Char(string='Vapi Buton Basligi', default='Yapay Zekayi Ara')
    vapi_cta_subtitle = fields.Char(string='Vapi Buton Alt Basligi', default='Sohbet veya sesli destek')
    vapi_page_ids = fields.Many2many(
        'website.page',
        'ronix_quality_location_website_page_rel',
        'location_id',
        'page_id',
        string='Vapi Sayfalari',
        help='Secilirse Vapi sadece bu sayfalarda gosterilir.',
    )
    vapi_color_base = fields.Char(string='Tema Ana Renk', default='#F8FAFC')
    vapi_color_accent = fields.Char(string='Tema Vurgu Rengi', default='#0F766E')
    vapi_color_button_base = fields.Char(string='Buton Ana Rengi', default='#0F172A')
    vapi_color_button_accent = fields.Char(string='Buton Vurgu Rengi', default='#F8FAFC')
    vapi_color_icon = fields.Char(string='Baslatici Ikon Rengi', default='#F8FAFC')
    vapi_offset_top_px = fields.Integer(string='Bilesen Ust Boslugu (px)', default=88)
    vapi_offset_right_px = fields.Integer(string='Bilesen Sag Boslugu (px)', default=24)
    gemini_enabled = fields.Boolean(default=False, string='Gemini Entegrasyonu')
    gemini_api_key = fields.Char(string='Gemini API Key')
    gemini_model = fields.Char(string='Gemini Model', default='gemini-2.5-pro')
    gemini_project_id = fields.Char(string='Gemini Project ID')
    gemini_location = fields.Char(string='Gemini Region', default='us-central1')
    gemini_system_prompt = fields.Text(string='Gemini System Prompt')
    gemini_temperature = fields.Float(string='Gemini Temperature', default=0.2, digits=(16, 2))
    gemini_top_p = fields.Float(string='Gemini Top P', default=0.95, digits=(16, 2))
    gemini_top_k = fields.Integer(string='Gemini Top K', default=40)
    gemini_max_output_tokens = fields.Integer(string='Gemini Max Output Tokens', default=2048)
    gemini_use_vertex_ai = fields.Boolean(string='Vertex AI Kullan')

    _sql_constraints = [
        ('ronix_quality_location_token_unique', 'unique(token)', 'Lokasyon tokeni benzersiz olmalidir.'),
    ]

    @api.model
    def _get_single_active_location_id(self):
        locations = self.search([('active', '=', True)], limit=2, order='id asc')
        return locations.id if len(locations) == 1 else False

    @api.depends('button_ids')
    def _compute_button_count(self):
        for record in self:
            record.button_count = len(record.button_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            token = vals.get('token')
            if token:
                token = str(token).strip()
            if token:
                vals['token'] = token
            else:
                vals['token'] = self._generate_unique_token()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('token'):
            vals = dict(vals, token=str(vals['token']).strip())
        return super().write(vals)

    @api.constrains('token')
    def _check_token(self):
        for record in self:
            token = (record.token or '').strip()
            if not token:
                raise ValidationError('Lokasyon tokeni zorunludur.')
            if any(char.isspace() for char in token):
                raise ValidationError('Lokasyon tokeni bosluk iceremez.')

    @api.constrains('vapi_offset_top_px', 'vapi_offset_right_px')
    def _check_vapi_offsets(self):
        for record in self:
            if record.vapi_offset_top_px < 0 or record.vapi_offset_right_px < 0:
                raise ValidationError('Vapi bilesen bosluklari negatif olamaz.')

    @api.constrains('gemini_temperature', 'gemini_top_p', 'gemini_top_k', 'gemini_max_output_tokens')
    def _check_gemini_values(self):
        for record in self:
            if record.gemini_temperature < 0 or record.gemini_temperature > 2:
                raise ValidationError('Gemini temperature 0 ile 2 arasinda olmalidir.')
            if record.gemini_top_p < 0 or record.gemini_top_p > 1:
                raise ValidationError('Gemini top p 0 ile 1 arasinda olmalidir.')
            if record.gemini_top_k < 0:
                raise ValidationError('Gemini top k negatif olamaz.')
            if record.gemini_max_output_tokens < 1:
                raise ValidationError('Gemini max output tokens en az 1 olmalidir.')

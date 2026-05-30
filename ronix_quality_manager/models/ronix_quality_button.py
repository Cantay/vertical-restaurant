import secrets
import string
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


LANG_PREFIX_PATTERN = re.compile(r'^/[a-z]{2}(?:_[A-Z]{2})?(?=/|$)')


class RonixQualityButton(models.Model):
    _name = 'ronix.quality.button'
    _description = 'Ronix Quality Button'
    _order = 'sequence asc, id asc'

    def init(self):
        # Upgrade path: preserve previously generated route keys as editable routes.
        self._cr.execute("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'ronix_quality_button'
               AND column_name IN ('mobile_route', 'route_key')
        """)
        columns = {row[0] for row in self._cr.fetchall()}
        if {'mobile_route', 'route_key'}.issubset(columns):
            self._cr.execute("""
                UPDATE ronix_quality_button
                   SET mobile_route = '/ronix-quality-' || route_key
                 WHERE (mobile_route IS NULL OR mobile_route = '')
                   AND route_key IS NOT NULL
                   AND route_key != ''
            """)

    name = fields.Char(string='Buton Adi', required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    icon_image = fields.Image(string='Buton Ikonu', max_width=512, max_height=512)
    menu_type = fields.Selection(
        [
            ('main', 'Ana Menu Ikonu'),
            ('side', 'Yan Menu Ikonu'),
        ],
        string='Menu Turu',
        required=True,
        default='main',
        tracking=True,
    )
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    mobile_route = fields.Char(
        string='Mobil Rota',
        required=True,
        copy=False,
        index=True,
        tracking=True,
        default=lambda self: self._generate_default_mobile_route(),
    )
    public_url = fields.Char(
        string='Herkese Acik URL',
        compute='_compute_public_url',
    )

    _sql_constraints = [
        ('ronix_quality_button_mobile_route_unique', 'unique(mobile_route)', 'Mobil rota benzersiz olmalidir.'),
    ]

    @api.model
    def _generate_unique_route_key(self):
        alphabet = string.ascii_letters + string.digits
        for _attempt in range(20):
            route_key = ''.join(secrets.choice(alphabet) for _index in range(8))
            route_path = '/ronix-quality-%s' % route_key
            if not self.search_count([('mobile_route', '=', route_path)]):
                return route_key
        raise ValidationError('Benzersiz bir mobil rota anahtari olusturulamadi.')

    @api.model
    def _generate_default_mobile_route(self):
        return '/ronix-quality-%s' % self._generate_unique_route_key()

    @api.depends('mobile_route')
    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        for record in self:
            record.public_url = '%s%s' % (base_url, record.mobile_route) if base_url else record.mobile_route

    @api.model
    def _normalize_mobile_route(self, mobile_route):
        route = (mobile_route or '').strip()
        if not route:
            return False
        if not route.startswith('/'):
            route = '/' + route
        while '//' in route:
            route = route.replace('//', '/')
        return route

    @api.model
    def _get_request_path_candidates(self, request_path):
        normalized_path = self._normalize_mobile_route(request_path)
        if not normalized_path:
            return []

        candidates = []

        def _append_candidate(route):
            if route and route not in candidates:
                candidates.append(route)

        _append_candidate(normalized_path)
        if normalized_path != '/':
            base_path = normalized_path.rstrip('/') or '/'
            _append_candidate(base_path)
            _append_candidate('%s/' % base_path)

        lang_free_path = LANG_PREFIX_PATTERN.sub('', normalized_path, count=1) or '/'
        lang_free_path = self._normalize_mobile_route(lang_free_path)
        if lang_free_path and lang_free_path != normalized_path:
            _append_candidate(lang_free_path)
            if lang_free_path != '/':
                base_path = lang_free_path.rstrip('/') or '/'
                _append_candidate(base_path)
                _append_candidate('%s/' % base_path)

        return candidates

    @api.model
    def get_button_for_request_path(self, request_path):
        for route in self._get_request_path_candidates(request_path):
            button = self.sudo().search([
                ('mobile_route', '=', route),
                ('active', '=', True),
                ('location_id.active', '=', True),
            ], limit=1)
            if button:
                return button
        return self.browse()

    def copy(self, default=None):
        if default is None:
            default = {}
        
        new_button = super().copy(default)
        
        if self.mobile_route and new_button.mobile_route:
            existing_page = self.env['website.page'].sudo().search([('url', '=', self.mobile_route)], limit=1)
            if existing_page:
                clean_route = new_button.mobile_route.strip('/').replace('-', '_')
                new_key = f'ronix_quality_manager.{clean_route}'
                existing_page.copy({
                    'url': new_button.mobile_route,
                    'name': f"{existing_page.name} (Copy)",
                    'key': new_key,
                    'is_published': False,
                })
                
        return new_button

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('mobile_route'):
                vals['mobile_route'] = self._normalize_mobile_route(vals['mobile_route'])
            elif not vals.get('mobile_route'):
                vals['mobile_route'] = self._generate_default_mobile_route()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('mobile_route'):
            vals = dict(vals, mobile_route=self._normalize_mobile_route(vals['mobile_route']))
        res = super().write(vals)
        if 'active' in vals:
            for record in self:
                pages = self.env['website.page'].sudo().search([('url', '=', record.mobile_route)])
                if pages:
                    pages.write({'is_published': vals['active']})
        return res

    def unlink(self):
        urls = self.mapped('mobile_route')
        res = super().unlink()
        if urls:
            pages = self.env['website.page'].sudo().search([('url', 'in', urls)])
            if pages:
                pages.unlink()
        return res

    @api.constrains('mobile_route')
    def _check_mobile_route(self):
        for record in self:
            mobile_route = (record.mobile_route or '').strip()
            if not mobile_route:
                raise ValidationError('Mobil rota zorunludur.')
            if not mobile_route.startswith('/'):
                raise ValidationError('Mobil rota / ile baslamalidir.')
            if any(char.isspace() for char in mobile_route):
                raise ValidationError('Mobil rota bosluk iceremez.')

    def action_open_mobile_route(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.public_url,
            'target': 'new',
        }

import re
from uuid import uuid4

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request


LANG_PREFIX_PATTERN = re.compile(r"^/[a-z]{2}(?:_[A-Z]{2})?(?=/|$)")
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class RonixPwaApp(models.Model):
    _name = "ronix.pwa.app"
    _description = "Ronix PWA App"
    _order = "sequence asc, id asc"

    name = fields.Char(required=True, tracking=True)
    short_name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    website_id = fields.Many2one(
        "website",
        string="Website",
        required=True,
        default=lambda self: self.env["website"].get_current_website(),
        ondelete="cascade",
        tracking=True,
    )
    match_path = fields.Char(
        string="Match Path",
        required=True,
        tracking=True,
        help="Website path that activates this PWA. Example: /ronix/mobile",
    )
    match_mode = fields.Selection(
        [
            ("exact", "Exact Path"),
            ("prefix", "Path Prefix"),
        ],
        string="Match Mode",
        required=True,
        default="prefix",
        tracking=True,
    )
    start_url = fields.Char(
        string="Start URL",
        required=True,
        default="/",
        tracking=True,
        help="URL opened when the installed app starts.",
    )
    scope_path = fields.Char(
        string="Scope",
        required=True,
        default="/",
        tracking=True,
        help="Only pages inside this path belong to this installed app.",
    )
    display = fields.Selection(
        [
            ("standalone", "Standalone"),
            ("fullscreen", "Fullscreen"),
            ("minimal-ui", "Minimal UI"),
            ("browser", "Browser"),
        ],
        string="Display Mode",
        required=True,
        default="standalone",
        tracking=True,
    )
    description = fields.Char(tracking=True)
    theme_color = fields.Char(default="#9f1d35", tracking=True)
    background_color = fields.Char(default="#ffffff", tracking=True)
    button_label = fields.Char(default="Uygulamayı Ekle", tracking=True)
    install_button_enabled = fields.Boolean(default=True, tracking=True)
    install_button_path = fields.Char(
        string="Install Button Path",
        tracking=True,
        help="Page path where the install button should appear. Leave empty to use the Start URL.",
    )
    install_button_match_mode = fields.Selection(
        [
            ("exact", "Exact Path"),
            ("prefix", "Path Prefix"),
        ],
        string="Install Button Match Mode",
        required=True,
        default="exact",
        tracking=True,
    )
    icon_image = fields.Image(
        string="App Icon",
        required=True,
        max_width=1024,
        max_height=1024,
    )
    app_uid = fields.Char(
        string="App ID",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: str(uuid4()),
    )
    manifest_url = fields.Char(
        string="Manifest URL",
        compute="_compute_urls",
    )
    service_worker_url = fields.Char(
        string="Service Worker URL",
        compute="_compute_urls",
    )
    public_start_url = fields.Char(
        string="Public Start URL",
        compute="_compute_urls",
    )

    _sql_constraints = [
        ("ronix_pwa_app_uid_unique", "unique(app_uid)", "App ID must be unique."),
    ]

    @api.depends("start_url")
    def _compute_urls(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")
        for record in self:
            record.manifest_url = f"/ronix/pwa/{record.id}/manifest.webmanifest" if record.id else False
            record.service_worker_url = f"/ronix/pwa/{record.id}/service-worker.js" if record.id else False
            record.public_start_url = f"{base_url}{record.start_url}" if base_url and record.start_url else record.start_url

    @api.model
    def _normalize_path(self, path):
        value = (path or "").strip()
        if not value:
            return "/"
        if not value.startswith("/"):
            value = "/" + value
        while "//" in value:
            value = value.replace("//", "/")
        if len(value) > 1 and value.endswith("/"):
            value = value.rstrip("/")
        return value or "/"

    @api.model
    def _normalize_match_path(self, path):
        return self._normalize_path(path)

    @api.model
    def _normalize_scope_path(self, path):
        return self._normalize_path(path)

    @api.model
    def _normalize_start_url(self, path):
        return self._normalize_path(path)

    @api.model
    def _normalize_install_button_path(self, path):
        return self._normalize_path(path)

    @api.model
    def _path_matches_prefix(self, request_path, prefix_path):
        request_path = self._normalize_path(request_path)
        prefix_path = self._normalize_path(prefix_path)
        if prefix_path == "/":
            return True
        return request_path == prefix_path or request_path.startswith(prefix_path + "/")

    @api.model
    def _path_is_within_scope(self, path, scope_path):
        return self._path_matches_prefix(path, scope_path)

    @api.model
    def _candidate_paths(self, request_path):
        normalized = self._normalize_path(request_path)
        candidates = [normalized]
        lang_free = self._normalize_path(LANG_PREFIX_PATTERN.sub("", normalized, count=1) or "/")
        if lang_free not in candidates:
            candidates.append(lang_free)
        return candidates

    @api.model
    def _record_matches_request_path(self, record, request_path):
        request_path = self._normalize_path(request_path)
        match_path = self._normalize_match_path(record.match_path)
        if record.match_mode == "exact":
            return request_path == match_path
        return self._path_matches_prefix(request_path, match_path)

    @api.model
    def _request_cache(self):
        try:
            cache = getattr(request, "_ronix_pwa_manager_cache", None)
        except RuntimeError:
            return None
        if cache is None:
            cache = {}
            request._ronix_pwa_manager_cache = cache
        return cache

    @api.model
    def get_pwa_for_request_path(self, request_path, website=False):
        website = website or self.env["website"].get_current_website()
        normalized_path = self._normalize_path(request_path)
        cache_key = ("ronix_pwa_app", website.id, normalized_path)
        cache = self._request_cache()
        if cache and cache_key in cache:
            return cache[cache_key]

        apps = self.sudo().search(
            [
                ("active", "=", True),
                ("website_id", "=", website.id),
            ]
        )
        matches = []
        for app in apps:
            for candidate in self._candidate_paths(request_path):
                if self._record_matches_request_path(app, candidate):
                    matches.append(app)
                    break
        if not matches:
            app = self.browse()
        else:
            matches = sorted(
                matches,
                key=lambda app: (
                    0 if app.match_mode == "exact" else 1,
                    -len(self._normalize_match_path(app.match_path)),
                    app.sequence,
                    app.id,
                ),
            )
            app = matches[0]

        if cache is not None:
            cache[cache_key] = app
        return app

    def should_show_install_button_for_request_path(self, request_path):
        self.ensure_one()
        if not self.install_button_enabled:
            return False

        request_candidates = self._candidate_paths(request_path)
        button_path = self._normalize_install_button_path(self.install_button_path or self.start_url)
        for candidate in request_candidates:
            if self.install_button_match_mode == "exact" and candidate == button_path:
                return True
            if self.install_button_match_mode == "prefix" and self._path_matches_prefix(candidate, button_path):
                return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for vals in vals_list:
            vals = dict(vals)
            vals["match_path"] = self._normalize_match_path(vals.get("match_path"))
            vals["start_url"] = self._normalize_start_url(vals.get("start_url") or vals["match_path"])
            vals["scope_path"] = self._normalize_scope_path(vals.get("scope_path") or vals["match_path"])
            if vals.get("install_button_path"):
                vals["install_button_path"] = self._normalize_install_button_path(vals.get("install_button_path"))
            prepared_vals_list.append(vals)
        return super().create(prepared_vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "match_path" in vals:
            vals["match_path"] = self._normalize_match_path(vals.get("match_path"))
        if "start_url" in vals:
            vals["start_url"] = self._normalize_start_url(vals.get("start_url"))
        if "scope_path" in vals:
            vals["scope_path"] = self._normalize_scope_path(vals.get("scope_path"))
        if "install_button_path" in vals and vals.get("install_button_path"):
            vals["install_button_path"] = self._normalize_install_button_path(vals.get("install_button_path"))
        return super().write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault("app_uid", str(uuid4()))
        default.setdefault("name", f"{self.name} (Copy)")
        return super().copy(default)

    @api.constrains("match_path", "start_url", "scope_path", "install_button_path")
    def _check_paths(self):
        for record in self:
            path_values = [record.match_path, record.start_url, record.scope_path]
            if record.install_button_path:
                path_values.append(record.install_button_path)
            for value in path_values:
                if not value:
                    raise ValidationError("Path values are required.")
                if not value.startswith("/"):
                    raise ValidationError("All path values must start with '/'.")
                if any(char.isspace() for char in value):
                    raise ValidationError("Path values cannot contain spaces.")
            if not record._path_is_within_scope(record.start_url, record.scope_path):
                raise ValidationError("Start URL must stay inside the declared scope.")
            if record.install_button_enabled:
                button_path = record._normalize_install_button_path(record.install_button_path or record.start_url)
                if not record._path_is_within_scope(button_path, record.scope_path):
                    raise ValidationError("Install button path must stay inside the declared scope.")

    @api.constrains("theme_color", "background_color")
    def _check_colors(self):
        for record in self:
            for color in (record.theme_color, record.background_color):
                if color and not HEX_COLOR_PATTERN.match(color):
                    raise ValidationError("Colors must be written in HEX format, for example #A1122F.")

    @api.constrains("website_id", "match_path", "match_mode", "active")
    def _check_unique_route_per_website(self):
        for record in self.filtered("active"):
            domain = [
                ("id", "!=", record.id),
                ("active", "=", True),
                ("website_id", "=", record.website_id.id),
                ("match_path", "=", record.match_path),
                ("match_mode", "=", record.match_mode),
            ]
            if self.search_count(domain):
                raise ValidationError("There is already an active PWA using the same website, path, and match mode.")

    def action_open_start_url(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.public_start_url or self.start_url,
            "target": "new",
        }

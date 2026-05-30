import base64
import json

from odoo import http, tools
from odoo.http import request


class RonixPwaController(http.Controller):
    def _get_app(self, pwa_app_id):
        if not request.env.registry.models.get("ronix.pwa.app"):
            return False
        return request.env["ronix.pwa.app"].sudo().browse(pwa_app_id).exists().filtered("active")[:1]

    def _public_base_url(self):
        return request.httprequest.url_root.rstrip("/")

    @http.route("/ronix/pwa/<int:pwa_app_id>/manifest.webmanifest", type="http", auth="public", website=True, sitemap=False)
    def ronix_pwa_manifest(self, pwa_app_id, **kwargs):
        app = self._get_app(pwa_app_id)
        if not app:
            return request.not_found()

        base_url = self._public_base_url()
        manifest = {
            "id": app.app_uid,
            "name": app.name,
            "short_name": app.short_name,
            "description": app.description or "",
            "start_url": app.start_url,
            "scope": app.scope_path,
            "display": app.display,
            "theme_color": app.theme_color or "#9f1d35",
            "background_color": app.background_color or "#ffffff",
            "prefer_related_applications": False,
            "icons": [
                {
                    "src": f"{base_url}/ronix/pwa/{app.id}/icon/192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any",
                },
                {
                    "src": f"{base_url}/ronix/pwa/{app.id}/icon/512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any",
                },
                {
                    "src": f"{base_url}/ronix/pwa/{app.id}/icon/512-maskable.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable",
                },
            ],
        }
        body = json.dumps(manifest, ensure_ascii=False)
        headers = [
            ("Content-Type", "application/manifest+json; charset=utf-8"),
            ("Cache-Control", "public, max-age=300"),
        ]
        return request.make_response(body, headers=headers)

    @http.route("/ronix/pwa/<int:pwa_app_id>/service-worker.js", type="http", auth="public", website=True, sitemap=False)
    def ronix_pwa_service_worker(self, pwa_app_id, **kwargs):
        app = self._get_app(pwa_app_id)
        if not app:
            return request.not_found()

        version = str(int(app.write_date.timestamp())) if app.write_date else "1"
        cache_prefix = f"ronix-pwa-{app.id}-"
        cache_name = f"{cache_prefix}{version}"
        assets = [
            app.start_url,
            f"/ronix/pwa/{app.id}/manifest.webmanifest",
            f"/ronix/pwa/{app.id}/icon/192.png",
            f"/ronix/pwa/{app.id}/icon/512.png",
            f"/ronix/pwa/{app.id}/icon/512-maskable.png",
        ]
        body = f"""
const CACHE_PREFIX = {json.dumps(cache_prefix)};
const CACHE_NAME = {json.dumps(cache_name)};
const START_URL = {json.dumps(app.start_url)};
const PRECACHE_URLS = {json.dumps(assets)};

self.addEventListener("install", (event) => {{
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .catch(() => null)
            .then(() => self.skipWaiting())
    );
}});

self.addEventListener("activate", (event) => {{
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys
                .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
                .map((key) => caches.delete(key))
        )).then(() => self.clients.claim())
    );
}});

self.addEventListener("fetch", (event) => {{
    if (event.request.method !== "GET") {{
        return;
    }}

    if (event.request.mode === "navigate") {{
        event.respondWith(
            fetch(event.request).catch(() => caches.match(START_URL))
        );
        return;
    }}

    const requestUrl = new URL(event.request.url);
    if (requestUrl.origin !== self.location.origin) {{
        return;
    }}

    event.respondWith(
        fetch(event.request)
            .then((response) => {{
                const cloned = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, cloned)).catch(() => null);
                return response;
            }})
            .catch(() => caches.match(event.request))
    );
}});
""".strip()
        headers = [
            ("Content-Type", "application/javascript; charset=utf-8"),
            ("Cache-Control", "no-cache"),
            ("Service-Worker-Allowed", app.scope_path or "/"),
        ]
        return request.make_response(body, headers=headers)

    @http.route(
        [
            "/ronix/pwa/<int:pwa_app_id>/icon/<int:size>.png",
            "/ronix/pwa/<int:pwa_app_id>/icon/<int:size>-maskable.png",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def ronix_pwa_icon(self, pwa_app_id, size=512, **kwargs):
        app = self._get_app(pwa_app_id)
        if not app or not app.icon_image:
            return request.not_found()

        size = min(max(int(size or 512), 32), 1024)
        source = base64.b64decode(app.icon_image)
        image = tools.image_process(
            source,
            size=(size, size),
            crop="center",
            output_format="PNG",
        )
        headers = [
            ("Content-Type", "image/png"),
            ("Cache-Control", "public, max-age=300"),
        ]
        return request.make_response(image, headers=headers)

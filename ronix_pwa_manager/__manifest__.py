{
    "name": "Ronix PWA Manager",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Website yolları için özel isim, ikon ve manifest ile PWA oluşturma",
    "description": """Odoo website üzerinde belirli URL yolları için kurulabilir PWA uygulamaları tanımlar.
Her PWA için özel ad, kısa ad, ikon, tema rengi, arka plan rengi ve başlangıç URL'i yönetir.
Dinamik manifest endpointleriyle her uygulama için ayrı manifest dosyası üretir.
Frontend kurulum butonu ve install prompt akışıyla kullanıcıya kolay kurulum deneyimi sunar.
Birden fazla marka, lokasyon veya web uygulamasını aynı website içinde ayrı PWA olarak yayınlar.""",
    "author": "Odoo Custom",
    "depends": ["website"],
    "data": [
        "security/ir.model.access.csv",
        "views/ronix_pwa_app_views.xml",
        "views/menus.xml",
        "views/ronix_pwa_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ronix_pwa_manager/static/src/js/ronix_pwa_install.js",
            "ronix_pwa_manager/static/src/scss/ronix_pwa_install.scss",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

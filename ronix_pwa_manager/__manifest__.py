{
    "name": "Ronix PWA Yönetimi",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Belirli website yolları için özel ad ve ikonlu PWA uygulamaları oluşturur",
    "description": """
Ronix PWA Yönetimi
==================
Belirli website yolları için ayrı ad, ikon, manifest dosyası
ve kurulum butonu içeren yüklenebilir PWA uygulamaları oluşturur.
""",
    "author": "Cantay Aktura",
    "website": "https://www.lugatsoft.com",
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

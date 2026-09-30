{
    "name": "Ronix PWA Manager",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Website yolları için özel isim, ikon ve manifest ile PWA oluşturma",
    "description": """
Ronix PWA Manager
=================

Bu modül, Odoo website üzerinde belirli URL yolları için kurulabilir PWA
uygulamaları tanımlamayı sağlar. Her uygulama için özel ad, kısa ad, ikon,
renkler, başlangıç URL'i ve manifest dosyası üretilebilir; frontend tarafında
uygun sayfalarda PWA kurulum butonu gösterilir.

Öne çıkan özellikler:

* Website yolu bazlı PWA uygulama kayıtları.
* Uygulama adı, kısa ad, ikon, tema rengi, arka plan rengi ve başlangıç URL'i
  yönetimi.
* Dinamik manifest endpointleriyle her PWA için ayrı manifest üretimi.
* Frontend kurulum butonu, install prompt yakalama ve kullanıcı dostu kurulum
  akışı.
* Website içinde birden fazla marka, lokasyon veya uygulama deneyimini ayrı PWA
  olarak yayınlama.
""",
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

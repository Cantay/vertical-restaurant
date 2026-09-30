{
    'name': 'Ronix QR Menu',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'QR kodlu dijital menü, AR ürün görüntüleme, garson çağırma ve besin bilgisi',
    'description': """
Ronix QR Menu
=============

Bu modül, restoranlar için QR kod tabanlı dijital menü sistemi sağlar. Her
masa için QR kod üretilebilir; müşteriler kategori ve ürünleri web üzerinden
görüntüleyebilir, ürün detaylarında içerik, alerjen, besin değeri ve 3D/AR
görünüm bilgilerine ulaşabilir.

Öne çıkan özellikler:

* Restoran, masa, kategori, ürün ve alerjen kayıtları için backend yönetimi.
* Masa bazlı QR kod oluşturma ve QR menü URL'i üretme.
* Kategori ve ürünlerden oluşan mobil uyumlu dijital menü sayfaları.
* Ürün içerikleri, alerjenler, kalori/besin bilgileri ve detay açıklamaları.
* 3D model-viewer ile AR ürün görüntüleme desteği.
* Garson çağırma sistemi ve backend tarafında çağrı takibi.
* Frontend QR menü, ürün detay sayfası, AR görüntüleyici ve garson çağırma
  JavaScript bileşenleri.
    """,
    'author': 'Lugatsoft',
    'website': 'https://www.lugatsoft.com',
    'depends': [
        'base',
        'mail',
        'website',
        'sale',
    ],
    'data': [
        # Security
        'security/ronix_qr_menu_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Data
        'data/allergen_data.xml',
        # Backend Views
        'views/qr_menu_restaurant_views.xml',
        'views/qr_menu_table_views.xml',
        'views/qr_menu_category_views.xml',
        'views/qr_menu_item_views.xml',
        'views/qr_menu_allergen_views.xml',
        'views/qr_menu_waiter_call_views.xml',
        # Frontend Templates
        'views/qr_menu_templates.xml',
        'views/qr_menu_item_detail_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ronix_qr_menu/static/src/css/qr_menu.css',
            'ronix_qr_menu/static/src/js/qr_menu_main.js',
            'ronix_qr_menu/static/src/js/qr_ar_viewer.js',
            'ronix_qr_menu/static/src/js/qr_waiter_call.js',
        ],
        'web.assets_backend': [
            'ronix_qr_menu/static/src/js/qr_waiter_dashboard.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

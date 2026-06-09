{
    'name': 'Ronix QR Menü Entegrasyon Köprüsü',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Yemek teslimat ile QR menü modülleri arasında veri senkronizasyonu sağlar',
    'description': """
Ronix yemek teslimat ve QR menü modülleri arasındaki restoran,
kategori ve ürün verilerini ilişkilendirir.

- Tek tıkla veri senkronizasyonu yapar
- Puan, çalışma saati ve ürün detaylarını eşler
- QR menü sayfalarında restoran bilgilerini görünür hale getirir
    """,
    'author': 'Cantay Aktura',
    'website': 'https://www.lugatsoft.com',
    'depends': [
        'ronix_food_delivery',
        'ronix_qr_menu',
    ],
    'data': [
        'views/food_restaurant_views.xml',
        'views/qr_menu_restaurant_views.xml',
        'views/qr_menu_category_views.xml',
        'views/qr_menu_item_views.xml',
        'views/qr_menu_bridge_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ronix_qr_menu_bridge/static/src/css/bridge_styles.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

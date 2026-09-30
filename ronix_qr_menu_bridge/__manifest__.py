{
    'name': 'Ronix QR Menu Bridge',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Food Delivery ve QR Menu modülleri arasında veri eşleştirme köprüsü',
    'description': """Food Delivery ve QR Menu modülleri arasında restoran, kategori ve ürün verilerini eşleştirir.
Food Delivery restoranı ile QR Menü restoranını karşılıklı referans alanlarıyla bağlar.
Tek tıkla restoran bilgisi, çalışma saatleri, puanlar ve yorum sayılarını QR menüye aktarır.
Ürün eklentilerini QR menü içerik yapısına uygun şekilde senkronize eder.
QR menü frontend ekranlarında restoran puanı ve çalışma saati gösterimi sağlar.""",
    'author': 'Lugatsoft',
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

{
    'name': 'Ronix QR Menu Bridge',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Food Delivery ve QR Menu modülleri arasında veri eşleştirme köprüsü',
    'description': """
Ronix QR Menu Bridge
====================

Bu modül, Ronix Food Delivery ve Ronix QR Menu modülleri arasında restoran,
kategori ve ürün verilerini eşleştirir. Food Delivery tarafındaki restoran
bilgileri, çalışma saatleri, puanlar, yorum sayıları ve ürün eklentileri QR
menü tarafına aktarılabilir.

Öne çıkan özellikler:

* Food Delivery restoranı ile QR Menü restoranını birbirine bağlama.
* Kategori ve ürün kayıtları arasında karşılıklı referans alanları.
* Tek tıkla Food Delivery verilerini QR Menü restoranına aktarma.
* Restoran puanı, yemek puanı, yorum sayısı ve çalışma saatlerini QR menüde
  gösterme.
* Ürün eklentilerini QR menü içerik/ingredient yapısına uygun şekilde taşıma.
* QR menü frontend sayfalarında restoran puanı ve çalışma saati görünümü için
  ek şablon ve stil desteği.
    """,
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

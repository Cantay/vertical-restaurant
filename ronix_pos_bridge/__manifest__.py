{
    'name': 'Ronix POS Bridge',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Restaurant, Food Delivery ve QR Menu arasında restoran verisi senkronizasyonu',
    'description': """
Ronix POS Bridge
================

Bu modül, Odoo POS Restaurant, Ronix Food Delivery ve Ronix QR Menu
modülleri arasında restoran, kategori, ürün ve masa verilerinin birlikte
çalışmasını sağlar. POS yapılandırmaları ile online sipariş ve QR menü
kayıtlarını eşleştirerek restoran operasyonlarında tek veri kaynağına yakın
bir çalışma düzeni sunar.

Öne çıkan özellikler:

* POS yapılandırması, Food Delivery restoranı ve QR Menü restoranı arasında
  bağlantı alanları.
* POS kategorileri ile website ürün kategorilerini eşleştirme.
* Ürünlerde POS'ta kullanılabilirlik ve yemek ürünü işaretlerini senkronize
  etme.
* POS restoran masalarını QR Menü masa kayıtlarıyla eşleştirme.
* Restoran, kategori ve masa verileri için backend görünüm genişletmeleri.
* Food Delivery ve QR Menü köprüsüyle birlikte çalışan tamamlayıcı
  entegrasyon katmanı.
    """,
    'author': 'Lugatsoft',
    'website': 'https://www.lugatsoft.com',
    'depends': [
        'pos_restaurant',
        'ronix_food_delivery',
        'ronix_qr_menu',
        'ronix_qr_menu_bridge',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/food_restaurant_views.xml',
        'views/qr_menu_restaurant_views.xml',
        'views/restaurant_table_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

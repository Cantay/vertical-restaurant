{
    'name': 'Ronix POS Bridge',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Restaurant, Food Delivery ve QR Menu arasında restoran verisi senkronizasyonu',
    'description': """POS Restaurant, Food Delivery ve QR Menu modüllerini aynı restoran verisi etrafında birleştirir.
POS yapılandırması, online sipariş restoranı ve QR Menü restoranı arasında bağlantı kurar.
POS kategorileri ile website ürün kategorilerini eşleştirir.
Ürünlerde POS'ta kullanılabilirlik ve yemek ürünü işaretlerini senkronize eder.
Restoran masalarını QR Menü masa kayıtlarıyla eşleştirerek masa bazlı dijital menüyü destekler.
Restoran, kategori, ürün ve masa verileri için backend görünüm genişletmeleri sağlar.""",
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

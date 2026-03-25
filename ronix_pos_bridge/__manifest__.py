{
    'name': 'Ronix POS Bridge',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Bridge between POS Restaurant, Food Delivery, and QR Menu',
    'description': """
        Bidirectional sync between pos_restaurant, ronix_food_delivery, and ronix_qr_menu:
        - Restaurant linking (pos.config <-> food.restaurant <-> qr.menu.restaurant)
        - Category mapping (pos.category <-> product.public.category)
        - Product flag sync (available_in_pos, is_food)
        - Table sync (restaurant.table <-> qr.menu.table)
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

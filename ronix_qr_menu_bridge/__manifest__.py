{
    'name': 'Ronix QR Menu Bridge',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Bridge between Food Delivery and QR Menu modules',
    'description': """
        Links and syncs data between ronix_food_delivery and ronix_qr_menu:
        - Restaurant, Category, Product linking
        - One-click sync with ratings, work hours, addons-to-ingredients
        - Frontend rating and work hours display on QR menu pages
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

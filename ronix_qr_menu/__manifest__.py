{
    'name': 'Ronix QR Menu',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'QR Code Digital Menu with AR, Waiter Call & Nutrition Info',
    'description': """
        QR Code based digital menu system for restaurants.
        Features:
        - QR code generation per table
        - Digital menu with categories and items
        - Food ingredients, allergens, and nutrition info
        - AR product viewing (3D model-viewer)
        - Waiter call system with real-time notifications
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

# -*- coding: utf-8 -*-
{
    'name': 'Türkiye Sanal POS Ödeme Sistemi',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Türkiye bankaları için sanal POS, 3D Secure, taksit, iptal ve iade entegrasyonu',
    'description': """Türkiye'deki bankaların sanal POS sistemlerini Odoo ödeme altyapısına bağlar.
Akbank, Garanti BBVA, İş Bankası, Ziraat, Halkbank, Vakıfbank, Yapı Kredi, QNB Finansbank ve diğer sağlayıcıları destekler.
3D Secure, 3D Pay ve NonSecure ödeme akışları için ödeme sağlayıcı yapılandırması sunar.
Kategori bazlı taksit, ürün sayfasında taksit gösterimi ve ödeme sayfasında taksit seçimi sağlar.
Taksit farkını sepete yansıtır ve ödeme işlem kayıtları üzerinden raporlama yapar.
İptal, iade, durum sorgulama, sipariş tarihçesi, QR ödeme ve tekrarlanan ödeme akışlarını destekler.
Banka bazlı yevmiye kayıtları, webhook yönetimi, otomatik hata işleme ve kart BIN tespiti içerir.""",
    'author': 'Odoo Turkey Community',
    'website': 'https://github.com/mewebstudio/pos',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'account_payment',
        'payment',
        'sale',
        'product',
        'website_sale',
    ],
    'data': [
        # Security
        'security/turkey_pos_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/payment_provider_data.xml',
        'data/payment_method_data.xml',
        'data/bank_gateway_data.xml',
        'data/ir_cron_data.xml',
        # 'data/account_chart_data.xml',
        
        # Views
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'views/bank_gateway_views.xml',
        'views/installment_option_views.xml',
        'views/product_category_views.xml',
        'views/pos_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/payment_portal_templates.xml',
        'views/product_template_views.xml',
        'views/account_journal_views.xml',
        
        # Wizards
        'wizards/pos_refund_wizard_views.xml',
        
        # Report
        'report/pos_transaction_report.xml',
        'report/pos_transaction_report_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'turkey_pos_payment/static/src/js/payment_form.js',
            'turkey_pos_payment/static/src/js/installment_calculator.js',
            'turkey_pos_payment/static/src/scss/payment_portal.scss',
        ],
        'web.assets_backend': [
            'turkey_pos_payment/static/src/js/backend_dashboard.js',
            'turkey_pos_payment/static/src/scss/backend_style.scss',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.00,
    'currency': 'EUR',
    'support': 'https://github.com/mewebstudio/pos/issues',
}

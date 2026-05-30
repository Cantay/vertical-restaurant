# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ronix Cevrimici Form Yonetimi',
    'version': '18.0.1.0.0',
    'category': 'Operations',
    'summary': 'Lokasyon bazli dinamik cevrimici form yonetimi',
    'description': """
Ronix Cevrimici Form Yonetimi
=============================

Lokasyon bazli tekrar kullanilabilir formlar olusturun,
frontend uzerinde yayinlayin ve tum gonderimleri
yetki kontrollu sekilde backend tarafinda yonetin.
    """,
    'author': 'Odoo Custom',
    'depends': [
        'base',
        'website',
        'ronix_quality_manager',
    ],
    'data': [
        'security/ronix_online_form_security.xml',
        'security/ir.model.access.csv',
        'views/ronix_online_form_views.xml',
        'views/ronix_online_form_submission_views.xml',
        'views/menus.xml',
        'views/ronix_online_form_templates.xml',
        'report/ronix_online_form_submission_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ronix_online_form_manager/static/src/scss/ronix_online_form.scss',
            'ronix_online_form_manager/static/src/js/ronix_online_form_designer.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

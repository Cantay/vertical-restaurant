# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ronix Quality Manager',
    'version': '18.0.1.0.2',
    'category': 'Operations/Quality',
    'summary': 'Manage mobile app locations and menu buttons',
    'description': """
Ronix Quality Manager
===================
Provides a dedicated backend for mobile application menu management.

- Define mobile app locations with unique tokens
- Manage main menu and side menu buttons per location
- Expose public endpoints for mobile app button feeds
- Provide mobile-first hotel website snippets for webview apps
    """,
    'author': 'Odoo Custom',
    'depends': [
        'base',
        'website',
    ],
    'data': [
        'security/ronix_quality_security.xml',
        'security/ir.model.access.csv',
        'views/ronix_quality_location_views.xml',
        'views/ronix_quality_button_views.xml',
        'views/ronix_quality_information_views.xml',
        'views/ronix_quality_announcement_views.xml',
        'views/ronix_quality_training_views.xml',
        'views/ronix_quality_audit_checklist_views.xml',
        'views/ronix_quality_operational_nonconformity_views.xml',
        'views/ronix_quality_inspection_report_views.xml',
        'views/ronix_quality_product_tracking_views.xml',
        'views/ronix_quality_butchery_tracking_views.xml',
        'views/ronix_quality_goods_acceptance_views.xml',
        'views/ronix_quality_guest_complaint_report_views.xml',
        'views/ronix_quality_guest_complaint_result_views.xml',
        'views/ronix_quality_guest_complaint_import_wizard_views.xml',
        'views/ronix_quality_guest_complaint_analysis_wizard_views.xml',
        'views/ronix_quality_spreadsheet_views.xml',
        'views/menus.xml',
        'report/ronix_quality_operational_nonconformity_report.xml',
        'report/ronix_quality_product_tracking_report.xml',
        'report/ronix_quality_butchery_tracking_report.xml',
        'report/ronix_quality_goods_acceptance_report.xml',
        'views/ronix_quality_vapi_templates.xml',
        'views/snippets/ronix_quality_snippets.xml',
        'views/snippets/ronix_quality_snippet_options.xml',
        'views/ronix_quality_website_pages.xml',
        'views/ronix_quality_product_tracking_templates.xml',
        'views/ronix_quality_butchery_tracking_templates.xml',
        'views/ronix_quality_goods_acceptance_templates.xml',
        'views/ronix_quality_spreadsheet_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ronix_quality_manager/static/src/js/ronix_quality_backend_date_input.js',
        ],
        'web.assets_frontend': [
            'ronix_quality_manager/static/src/scss/ronix_quality_snippets.scss',
            'ronix_quality_manager/static/src/js/ronix_quality_guest_request.js',
            'ronix_quality_manager/static/src/js/ronix_quality_shell_mode.js',
            'ronix_quality_manager/static/src/js/ronix_quality_vip_header.js',
            'ronix_quality_manager/static/src/js/ronix_quality_frontend_search.js',
            'ronix_quality_manager/static/src/js/ronix_quality_audit_checklist.js',
            'ronix_quality_manager/static/src/js/ronix_quality_inspection_form.js',
            'ronix_quality_manager/static/src/js/ronix_quality_product_tracking_form.js',
            'ronix_quality_manager/static/src/js/ronix_quality_goods_acceptance_form.js',
            'ronix_quality_manager/static/src/js/ronix_quality_spreadsheet_editor.js',
        ],
        'website.assets_wysiwyg': [
            'ronix_quality_manager/static/src/scss/ronix_quality_snippets.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

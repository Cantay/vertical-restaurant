{
    "name": "Ronix PWA Manager",
    "version": "18.0.1.0.0",
    "category": "Website",
    "summary": "Create path-based PWAs with custom names and icons",
    "description": """
Ronix PWA Manager
=================
Create installable PWAs for specific website paths with dedicated names,
icons, manifest files, and install buttons.
""",
    "author": "Odoo Custom",
    "depends": ["website"],
    "data": [
        "security/ir.model.access.csv",
        "views/ronix_pwa_app_views.xml",
        "views/menus.xml",
        "views/ronix_pwa_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ronix_pwa_manager/static/src/js/ronix_pwa_install.js",
            "ronix_pwa_manager/static/src/scss/ronix_pwa_install.scss",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

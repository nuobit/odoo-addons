# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Web Responsive Apps Menu Flat",
    "summary": "Apps menu of web_responsive in the look of the Odoo 17 home menu.",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions SL, Xplordoo SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "web_app_icon_flat",
        "web_responsive",
    ],
    "assets": {
        "web.assets_backend": [
            "web_responsive_apps_menu_flat/static/src/components/apps_menu/apps_menu.scss",
        ],
    },
    "auto_install": True,
}

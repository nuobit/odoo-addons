# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Web Responsive App Icon Flat",
    "summary": "Glue module between web_app_icon_flat and web_responsive.",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "web_app_icon_flat",
        "web_responsive",
    ],
    "assets": {
        "web.assets_backend": [
            "web_responsive_app_icon_flat/static/src/components/apps_menu/apps_menu.scss",
        ],
    },
    "auto_install": True,
}

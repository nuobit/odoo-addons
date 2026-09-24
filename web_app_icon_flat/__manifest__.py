# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Web App Icon Flat",
    "summary": "Show Odoo's flat app icons of version 17 and later",
    "version": "16.0.1.0.0",
    "category": "Web",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        "views/ir_module_module_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_app_icon_flat/static/src/js/flat_icon_url.esm.js",
            "web_app_icon_flat/static/src/js/settings_form_compiler.esm.js",
        ],
        "web.qunit_suite_tests": [
            "web_app_icon_flat/static/tests/*.esm.js",
        ],
    },
}

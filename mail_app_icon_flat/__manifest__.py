# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Mail App Icon Flat",
    "summary": "Glue module between web_app_icon_flat and mail.",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions SL, Xplordoo SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "mail",
        "web_app_icon_flat",
    ],
    "assets": {
        # The flat icon URLs are only in the session of the web client.
        "web.assets_backend": [
            "mail_app_icon_flat/static/src/models/*.esm.js",
        ],
        "web.qunit_suite_tests": [
            "mail_app_icon_flat/static/tests/*.esm.js",
        ],
    },
    "auto_install": True,
}

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Note App Icon Flat",
    "summary": "Glue module between web_app_icon_flat and note.",
    "version": "16.0.1.0.0",
    "category": "Hidden",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "note",
        "web_app_icon_flat",
    ],
    "assets": {
        # The flat icon URLs are only in the session of the web client.
        "web.assets_backend": [
            "note_app_icon_flat/static/src/components/**/*",
            "note_app_icon_flat/static/src/models/*.esm.js",
        ],
        "web.qunit_suite_tests": [
            "note_app_icon_flat/static/tests/*.esm.js",
        ],
    },
    "auto_install": True,
}

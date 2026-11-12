# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Mail Dictation",
    "summary": "Dictate messages in the chat composer instead of typing them.",
    "version": "16.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "NuoBiT Solutions SL, Xplordoo SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "mail",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "uninstall_hook": "uninstall_hook",
    "assets": {
        # The backend only: portal users and guests never load it.
        "web.assets_backend": [
            "mail_dictation/static/src/models/*.esm.js",
            "mail_dictation/static/src/components/*/*.xml",
            "mail_dictation/static/src/components/*/*.scss",
        ],
        "web.qunit_suite_tests": [
            "mail_dictation/static/tests/*.esm.js",
        ],
    },
}

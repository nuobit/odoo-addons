# Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Mail Dictation OpenAI",
    "summary": "Transcribe the chat dictation with an OpenAI-compatible service.",
    "version": "16.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "NuoBiT Solutions SL, Xplordoo SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "mail_dictation",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}

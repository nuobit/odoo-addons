# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Event Thin List",
    "version": "16.0.1.0.0",
    "category": "Website/Website",
    "summary": "Adds a thin list layout option for website events",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "website_event",
    ],
    "data": [
        "views/event_templates_list.xml",
        "views/snippets.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_event_thin_list/static/src/scss/event_template_list.scss",
        ],
    },
}

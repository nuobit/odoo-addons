# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Sale Rental Extension",
    "summary": "Adds kanban view, calendar and filters for rental positions.",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Rental",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale_rental",
    ],
    "data": [
        "views/sale_rental_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_rental_extension/static/src/scss/sale_rental_kanban.scss",
        ],
    },
}

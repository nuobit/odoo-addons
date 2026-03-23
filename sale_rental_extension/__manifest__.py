# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Sale Rental Extension",
    "summary": "Dedicated rental views, rental status tracking,"
    " kanban, calendar, configurable signature terms and translations.",
    "version": "16.0.1.2.0",
    "development_status": "Alpha",
    "category": "Rental",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale_rental",
    ],
    "data": [
        "views/sale_order_rental_views.xml",
        "views/res_config_settings_views.xml",
        "views/sale_rental_views.xml",
        "views/stock_picking_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_rental_extension/static/src/js/signature_widget.js",
            "sale_rental_extension/static/src/scss/sale_rental_kanban.scss",
            "sale_rental_extension/static/src/xml/signature_dialog.xml",
        ],
    },
}

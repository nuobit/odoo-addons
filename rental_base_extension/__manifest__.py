# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Rental Base Extension",
    "summary": "Dedicated rental views, rental status tracking,"
    " kanban, calendar, configurable signature terms and translations.",
    "version": "16.0.2.0.0",
    "development_status": "Alpha",
    "category": "Rental",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
    "depends": [
        "rental_base",
    ],
    "data": [
        "report/report_deliveryslip.xml",
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_picking_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "rental_base_extension/static/src/js/signature_widget.js",
            "rental_base_extension/static/src/scss/rental_kanban.scss",
            "rental_base_extension/static/src/xml/signature_dialog.xml",
        ],
    },
}

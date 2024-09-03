# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigesti-Odoo connector",
    "version": "14.0.1.1.11",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "connector_common",
        "partner_review",
        "sale_order_service",
        "sale_line_partner_description",
        "sale_specific_order_date",
        "oxigen_stock_alternate_lot",
    ],
    "external_dependencies": {
        "python": [
            "pymssql>=2.2.5,<2.3",
        ],
    },
    "data": [
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/oxigesti_backend_view.xml",
        "views/partner_view.xml",
        "views/product_product_view.xml",
        "views/product_category_view.xml",
        "views/product_buyerinfo_view.xml",
        "views/product_pricelist_item_view.xml",
        "views/stock_production_lot_view.xml",
        "views/sale_order_view.xml",
        "views/connector_oxigesti_menu.xml",
        "security/connector_oxigesti.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}

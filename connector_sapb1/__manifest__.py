# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector SAP B1",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "requests",
        ],
    },
    "depends": [
        "connector_extension",
        "sale_management",
    ],
    "data": [
        "security/connector_sapb1.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/sapb1_backend_view.xml",
        "views/sale_order_view.xml",
        "views/partner_view.xml",
        "views/product_product_view.xml",
        "views/connector_sapb1_menu.xml",
    ],
}

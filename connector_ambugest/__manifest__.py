# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Ambugest-Odoo connector",
    "version": "14.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "partner_review",
        "sale_order_service",
        "connector_common",
        "l10n_es",
        "sale_specific_order_date",
    ],
    "external_dependencies": {
        "python": [
            "pymssql",
        ],
    },
    "data": [
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/ambugest_backend_view.xml",
        "views/partner_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_view.xml",
        "views/connector_ambugest_menu.xml",
        "security/connector_ambugest.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector WooCommerce",
    "version": "14.0.0.1.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "external_dependencies": {
        "python": [
            "woocommerce",
        ],
    },
    "depends": [
        "connector_extension",
        "website_sale",
        "connector_wordpress",
    ],
    "data": [
        # "data/ir_cron.xml",
        # "data/queue_data.xml",
        # "data/queue_job_function_data.xml",
        "security/connector_woocommerce.xml",
        "security/ir.model.access.csv",
        "views/woocommerce_backend_view.xml",
        "views/connector_woocommerce_menu.xml",
    ],
    "installable": True,
}

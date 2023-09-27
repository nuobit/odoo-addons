# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector WooCommerce AST",
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
        "connector_woocommerce",
        "delivery_state",
    ],
    "data": ["security/ir.model.access.csv", "views/woocommerce_backend_view.xml"],
    "installable": True,
}

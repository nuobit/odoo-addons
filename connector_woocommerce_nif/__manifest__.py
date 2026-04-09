# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector WooCommerce NIF",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "external_dependencies": {
        "python": [
            "openupgradelib",
            "woocommerce",
        ],
    },
    "depends": [
        "connector_woocommerce",
    ],
    "pre_init_hook": "pre_init_hook",
}

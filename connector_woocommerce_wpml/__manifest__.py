# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Connector WooCommerce WMPL",
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
        # "connector_wordpress_wpml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/woocommerce_wpml_backend_view.xml",
        "views/product_attribute_value_views.xml",
        "views/product_attribute_views.xml",
        "views/product_product_views.xml",
        "views/product_public_category_views.xml",
        "views/product_template_views.xml",
        "views/connector_woocommerce_wpml_menu.xml",
    ],
    "installable": True,
}

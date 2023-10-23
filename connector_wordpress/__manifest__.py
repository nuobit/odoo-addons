# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector WordPress",
    "version": "14.0.0.1.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "connector_extension_wordpress",
        "website_sale_product_document",
    ],
    "data": [
        "security/connector_wordpress.xml",
        "security/ir.model.access.csv",
        "views/wordpress_backend_view.xml",
        "views/connector_wordpress_menu.xml",
    ],
    "installable": True,
}

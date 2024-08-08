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
    "external_dependencies": {
        # Python magic is included because it can detect more mimetypes
        # used to export the files to WordPress.
        "python": ["python-magic"],
    },
    "depends": [
        "connector_extension_wordpress",
        "website_sale_product_document",
        "tools_mimetypes_extension",
    ],
    "data": [
        "security/connector_wordpress.xml",
        "security/ir.model.access.csv",
        "views/ir_attachment_views.xml",
        "views/product_image_views.xml",
        "views/wordpress_backend_view.xml",
        "views/connector_wordpress_menu.xml",
    ],
    "installable": True,
}

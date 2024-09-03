# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Website Sale Variant",
    "version": "14.0.0.1.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Website",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "website_sale_variant",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/product_public_category.xml",
        "views/product_product.xml",
    ],
    "installable": True,
}

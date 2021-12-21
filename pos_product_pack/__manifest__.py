# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS product pack",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "Make the product pack feature available on POS.",
    "depends": [
        "point_of_sale",
        "sale_product_pack",
    ],
    "data": [
        "views/templates.xml",
    ],
    "qweb": [],
    "installable": True,
}

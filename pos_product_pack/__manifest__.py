# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS product pack",
    "version": "12.0.1.0.2",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "website": "https://github.com/OCA/pms",
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

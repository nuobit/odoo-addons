# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product supplier search",
    "summary": "Search products by supplier reference on "
    "selection fields and tree product view",
    "version": "12.0.1.0.0",
    "category": "Purchases",
    "author": "NuoBiT Solutions,S.L.,Eric Antones",
    "website": "https://github.com/OCA/pms",
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "views/product_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}

# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product supplier search",
    "summary": "Search products by supplier reference on "
    "selection fields and tree product view",
    "version": "16.0.0.0.0",
    "category": "Purchases",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "views/product_views.xml",
        "views/stock_picking_views.xml",
    ],
}

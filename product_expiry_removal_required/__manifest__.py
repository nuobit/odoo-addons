# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product Expiry Removal Required",
    "summary": "This module makes the lot removal date mandatory if the product has"
    " the expiry date enabled",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "product_expiry",
    ],
    "data": [
        "views/stock_lot_views.xml",
    ],
}

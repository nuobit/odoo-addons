# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions SL 2025 - Bijaya Kumal <bkumal@nuobit.com>
# Copyright NuoBiT Solutions SL 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock location tag",
    "summary": "This module adds tags on location",
    "author": "NuoBiT Solutions SL",
    "category": "Warehouse",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "security/stock_location_tag_security.xml",
        "security/ir.model.access.csv",
        "views/stock_location_views.xml",
        "views/stock_location_tag_views.xml",
    ],
}

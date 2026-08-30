# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Purchase order new line uom",
    "summary": "This module allows to edit the uom on new purchase "
    "order lines that don't have any invoice or stock move linked.",
    "author": "NuoBiT Solutions SL",
    "category": "Purchases",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "purchase",
        "purchase_stock",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
}

# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBit Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale line product description by partner",
    "summary": "This module allows to define multiple product description and code "
    "by partner and use it on sales",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_product_views.xml",
    ],
}

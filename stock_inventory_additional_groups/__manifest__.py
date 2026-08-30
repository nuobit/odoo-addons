# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock inventory additional groups",
    "summary": "This module adds adittional permission groups on inventory module",
    "author": "NuoBiT Solutions SL",
    "category": "Warehouse",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": ["security/stock_security.xml", "views/stock_quant_views.xml"],
}

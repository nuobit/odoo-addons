# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product unique barcode",
    "summary": "This module ensures that you enter a Unique Barcode for your Products",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "product",
    ],
    "pre_init_hook": "pre_init_hook_barcode_check",
}

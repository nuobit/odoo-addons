# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# Copyright NuoBiT 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product unique internal reference",
    "summary": "This module ensures that you enter a "
    "Unique Internal Reference (default_code) for your Products",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "product",
    ],
    "pre_init_hook": "internal_reference_duplicate_check",
}

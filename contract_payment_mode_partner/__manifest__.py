# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract Payment Mode Partner",
    "summary": "This module assigns the partner payment mode to the "
    "contract if it remains valid.",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["contract_payment_mode"],
    "category": "Sales Management",
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "data": ["views/contract_view.xml"],
}

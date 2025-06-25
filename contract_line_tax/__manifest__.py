# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract line tax",
    "summary": "This module adds taxes to lines and propagates it to invoice",
    "version": "17.0.1.0.1",
    "category": "Contract Management",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "account",
        "contract",
    ],
    "data": [
        "views/contract_view.xml",
    ],
    "installable": True,
}

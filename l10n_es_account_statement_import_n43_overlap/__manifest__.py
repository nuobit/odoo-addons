# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Bank statement import N43 overlap",
    "summary": "This module extends functionality of N43 bank statements"
    " checking overlapping dates",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "category": "Accounting & Finance",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_account_statement_import_n43",
    ],
    "data": [
        "wizards/account_bank_statement_import_view.xml",
    ],
    "auto_install": True,
}

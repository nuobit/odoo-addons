# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Bank statement import N43 overlap",
    "summary": "This module extends functionality of N43 bank statements checking overlapping dates",
    "version": "11.0.0.1.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Accounting & Finance",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_account_bank_statement_import_n43",
    ],
    "data": [
        "wizards/account_bank_statement_import_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}

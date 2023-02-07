# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract SII",
    "summary": "This module adds SII data to contracts and propagate them to invoice",
    "version": "14.0.1.0.1",
    "category": "Contract Management",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "contract",
        "l10n_es_aeat_sii_oca",
    ],
    "data": [
        "views/contract_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}

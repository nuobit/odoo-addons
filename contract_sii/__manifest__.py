# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Contract SII",
    "summary": "This module adds SII data to contracts and propagate them to invoice",
    "version": "18.0.1.0.0",
    "category": "Contract Management",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "contract",
        "l10n_es_aeat_sii_oca",
    ],
    "data": [
        "views/contract_view.xml",
    ],
}

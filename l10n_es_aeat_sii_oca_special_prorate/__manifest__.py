# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for SII",
    "summary": "This module adds special prorate template taxes to SII mapping",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL ",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_sii_oca",
    ],
    "data": [
        "data/l10n.es.aeat.map.tax.line.tax.csv",
        "data/aeat_sii_map_data.xml",
    ],
    "auto_install": True,
}

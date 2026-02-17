# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for 303",
    "summary": "This module adds the 303 model special prorate taxes",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_mod303",
    ],
    "data": [
        "data/l10n.es.aeat.map.tax.line.tax.csv",
        "data/l10n.es.aeat.map.tax.line.csv",
        "data/tax_code_map_mod303_2023_data.xml",
        "data/tax_code_map_mod303_202410_data.xml",
    ],
    "auto_install": True,
}

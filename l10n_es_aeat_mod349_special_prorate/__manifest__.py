# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for 349",
    "summary": "This module adds the 349 model special prorate taxes",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_mod349",
    ],
    "data": [
        "data/l10n.es.aeat.map.tax.line.tax.csv",
        "data/aeat_349_map_data.xml",
    ],
    "installable": True,
    "auto_install": True,
}

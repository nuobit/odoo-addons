# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for 349",
    "summary": "This module adds special prorate template taxes to the 349 model mapping",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_mod349",
    ],
    "data": [
        "data/aeat_349_map_data.xml",
    ],
    "installable": True,
    "auto_install": True,
}

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for 303",
    "summary": "This module adds the 303 model special prorate taxes",
    "version": "14.0.1.0.1",
    "category": "Sales",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_mod303",
    ],
    "data": [
        "data/tax_code_map_mod303_data.xml",
    ],
    "installable": True,
    "auto_install": True,
}

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "AEAT Modelo 349 Extension",
    "summary": "Extend AEAT Modelo 349 tax-template mappings",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod349",
        "l10n_es_extension",
    ],
    "data": [
        "data/aeat_349_map_data.xml",
    ],
    "auto_install": True,
}

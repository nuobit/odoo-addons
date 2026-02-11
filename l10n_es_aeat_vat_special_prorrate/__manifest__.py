# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT - Prorrata especial de IVA",
    "summary": "Módulo para gestionar la prorrata especial del IVA "
    "en las facturas de la AEAT",
    "version": "14.0.1.0.6",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303",
        "l10n_es_special_prorate",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/aeat_map_special_prorrate_year.xml",
        "views/aeat_map_special_prorrate_year_views.xml",
        "views/res_company_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}

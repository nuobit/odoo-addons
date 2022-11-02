# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT SII - Special Prorate Regularization Capital Asset",
    "summary": "This module allows send to SII automaticaly the "
    "capital assets prorate regularization.",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset",
        "l10n_es_aeat_sii_oca_extension",
    ],
    "data": [
        "data/aeat_sii_queue_job.xml",
        "views/account_asset.xml",
        "views/mod303_views.xml",
        "views/capital_asset_prorate_regularization.xml",
        "views/res_company_view.xml",
    ],
}

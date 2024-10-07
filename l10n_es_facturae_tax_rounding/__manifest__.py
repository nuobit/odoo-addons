# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "L10n ES Facturae Tax Rounding",
    "summary": "This module generates the Facturae with the tax amounts rounded "
    "according to the total tax amount by group.",
    "version": "14.0.0.0.0",
    "category": "Accounting & Finance",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["l10n_es_facturae"],
    "data": [
        "views/report_facturae.xml",
    ],
}

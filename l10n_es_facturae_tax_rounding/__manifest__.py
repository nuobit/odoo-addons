# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "L10n ES Facturae Tax Rounding",
    "summary": "This module generates the Facturae with the tax amounts rounded "
    "according to the total tax amount by group.",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["l10n_es_facturae"],
    "data": [
        "views/report_facturae.xml",
    ],
}

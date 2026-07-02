# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate templates",
    "summary": "This module adds special prorate taxes",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es",
        "account_chart_update"
        "l10n_es_vat_prorate",
    ],
    "data": [
        "views/account_tax_views.xml",
        # "wizards/account_chart_template_views.xml",
    ],
}

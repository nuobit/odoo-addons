# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate templates",
    "summary": "This module adds special prorate templates",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es",
        "account_template_view",
    ],
    "data": [
        "data/account_tax_data.xml",
        "data/account_fiscal_position_template_data.xml",
        "views/account_tax_views.xml",
        "views/account_chart_template_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Financial Report Multi Company",
    "summary": "This module allows to generate financial reports for multiple companies",
    "version": "14.0.0.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Accounting",
    "depends": ["account_financial_report"],
    "license": "AGPL-3",
    "data": [
        "wizards/trial_balance_wizard_views.xml",
        "report/templates/trial_balance.xml",
    ],
}

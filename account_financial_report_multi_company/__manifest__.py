# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Financial Report Multi Company",
    "summary": "This module allows to generate financial reports for multiple companies",
    "version": "16.0.0.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Accounting",
    "depends": ["account_financial_report"],
    "license": "AGPL-3",
    "data": [
        "wizards/trial_balance_wizard_views.xml",
        "report/templates/trial_balance.xml",
    ],
}

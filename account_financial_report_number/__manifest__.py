# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Account Financial Reports Number",
    "summary": "This module adds a filter to Journal Ledger "
    "report to filter by journal entry number",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "account_financial_report",
    ],
    "data": [
        "wizard/journal_ledger_wizard_view.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}

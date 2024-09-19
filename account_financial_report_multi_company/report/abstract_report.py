# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountFinancialAbstractReport(models.AbstractModel):
    _inherit = "report.account_financial_report.abstract_report"

    def _get_accounts_data(self, accounts_ids):
        accounts_data = super()._get_accounts_data(accounts_ids)
        accounts = self.env["account.account"].browse(accounts_ids)
        for account in accounts:
            accounts_data[account.id]["company"] = account.company_id.name
        return accounts_data

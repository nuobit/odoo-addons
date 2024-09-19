# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class TrialBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.trial_balance"

    def _get_groups_data(self, accounts_data, total_amount, foreign_currency):
        return super(TrialBalanceReport, self.sudo())._get_groups_data(
            accounts_data, total_amount, foreign_currency
        )

    def _get_hierarchy_groups(self, group_ids, groups_data, foreign_currency):
        groups_data = super()._get_hierarchy_groups(
            group_ids, groups_data, foreign_currency
        )
        for group_id in groups_data.keys():
            group = self.env["account.group"].browse(group_id)
            groups_data[group_id]["company"] = group.company_id.name
        return groups_data

    def _get_report_values(self, docids, data=None):
        company_ids = data.get("company_ids", [])
        if company_ids:
            self = self.with_context(company_ids=company_ids)
        return super(TrialBalanceReport, self)._get_report_values(docids, data)

    @api.model
    def _get_data(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        date_to,
        date_from,
        foreign_currency,
        only_posted_moves,
        show_partner_details,
        hide_account_at_0,
        unaffected_earnings_account,
        fy_start_date,
    ):
        company_ids = self.env.context.get("company_ids", [])
        total_amount, accounts_data, partners_data = {}, {}, []
        for company_id in company_ids:
            ta, ad, pd = super(TrialBalanceReport, self.sudo())._get_data(
                account_ids,
                journal_ids,
                partner_ids,
                company_id,
                date_to,
                date_from,
                foreign_currency,
                only_posted_moves,
                show_partner_details,
                hide_account_at_0,
                unaffected_earnings_account,
                fy_start_date,
            )
            total_amount.update(ta)
            accounts_data.update(ad)
            partners_data.extend(pd)
        return total_amount, accounts_data, partners_data

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero


class TrialBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.trial_balance"

    def _update_holding_company_domain(self, company, domain):
        company_ids = [company.id] + company.child_ids.ids
        found = False
        for i, (k, op, v) in enumerate(domain):
            if k == 'company_id':
                if found:
                    raise ValidationError(_("company_id found twice in domain %s") % domain)
                domain[i] = (k, 'in', company_ids)
                found = True
        if not found:
            domain.append(('company_id', 'in', company_ids))

    def _get_initial_balances_bs_ml_domain(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        date_from,
        only_posted_moves,
        show_partner_details,
    ):
        domain = super()._get_initial_balances_bs_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        company = self.env['res.company'].browse(company_id)
        if company.child_ids:
            self._update_holding_company_domain(company, domain)
        return domain

    def _get_initial_balances_pl_ml_domain(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        date_from,
        only_posted_moves,
        show_partner_details,
        fy_start_date,
    ):
        domain = super()._get_initial_balances_pl_ml_domain(account_ids,
                                                            journal_ids,
                                                            partner_ids,
                                                            company_id,
                                                            date_from,
                                                            only_posted_moves,
                                                            show_partner_details,
                                                            fy_start_date,
                                                            )
        company = self.env['res.company'].browse(company_id)
        if company.child_ids:
            self._update_holding_company_domain(company, domain)
        return domain

    @api.model
    def _get_period_ml_domain(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        date_to,
        date_from,
        only_posted_moves,
        show_partner_details,
    ):
        domain = super()._get_period_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            date_to,
            date_from,
            only_posted_moves,
            show_partner_details,
        )
        company = self.env['res.company'].browse(company_id)
        if company.child_ids:
            self._update_holding_company_domain(company, domain)
        return domain

    def _get_initial_balance_fy_pl_ml_domain(
        self,
        account_ids,
        journal_ids,
        partner_ids,
        company_id,
        fy_start_date,
        only_posted_moves,
        show_partner_details,
    ):
        domain = super()._get_initial_balance_fy_pl_ml_domain(
            account_ids,
            journal_ids,
            partner_ids,
            company_id,
            fy_start_date,
            only_posted_moves,
            show_partner_details,
        )
        company = self.env['res.company'].browse(company_id)
        if company.child_ids:
            self._update_holding_company_domain(company, domain)
        return domain

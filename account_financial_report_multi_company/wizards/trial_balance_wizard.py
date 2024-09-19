# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    @api.model
    def _get_company_domain(self):
        return [("id", "in", self.env.user.company_ids.ids)]

    company_ids = fields.Many2many(
        comodel_name="res.company",
        relation="trial_balance_report_wizard_company_rel",
        column1="trial_balance_report_wizard_id",
        column2="company_id",
        default=lambda self: self.env.company.ids,
        required=False,
        domain=lambda self: self._get_company_domain(),
        string="Companies",
    )

    def _prepare_report_trial_balance(self):
        data = super()._prepare_report_trial_balance()
        data["company_ids"] = self.company_ids.ids
        return data

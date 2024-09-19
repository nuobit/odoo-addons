# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models


class TrialBalanceXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_trial_balance_xlsx"

    def _get_report_columns(self, report):
        res = super()._get_report_columns(report)
        return {
            0: {
                "header": _("Company"),
                "field": "company",
                "width": 20,
            },
            **{key + 1: value for key, value in res.items()},
        }

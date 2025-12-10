# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax.repartition.line"

    @api.depends("factor_percent")
    def _compute_factor(self):
        res = super()._compute_factor()
        for rec in self:
            if rec.tax_id.prorate:
                tax_lines = rec.tax_id.invoice_repartition_line_ids.filtered(
                    lambda x: x.repartition_type == "tax"
                )
                lines_sum = sum(tax_lines.mapped("factor_percent"))

                if lines_sum == 200.0 or (len(tax_lines) == 3 and lines_sum == 100.0):
                    rec.factor = 0.0

        return res

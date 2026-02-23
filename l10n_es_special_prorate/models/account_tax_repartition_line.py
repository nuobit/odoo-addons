# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    @api.depends("factor_percent", "tax_id.prorate")
    def _compute_factor(self):
        res = super()._compute_factor()
        for rec in self:
            if rec.tax_id.prorate and rec.repartition_type == "tax":
                rec.factor = 0.0
        return res

# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    def get_prorrate_ratio(self, date, company_id):
        if self.repartition_type != "tax":
            return 1
        prorrate_map = self.env["aeat.map.special.prorrate.year"].search(
            [
                (
                    "company_id",
                    "=",
                    company_id or self.tax_id.company_id.id or self.env.company.id,
                ),
                ("year", "=", date.year),
            ]
        )
        if not prorrate_map:
            raise ValidationError(
                _("If a tax has prorate the year should exist on vat mapping")
            )

        prorate_ratio = prorrate_map.tax_percentage / 100
        if not self.account_id:
            prorate_ratio = 1 - prorate_ratio

        return prorate_ratio

    @api.depends("factor_percent")
    def _compute_factor(self):
        prorate = self.env.context.get("prorate")
        for record in self.filtered(
            lambda x: x.tax_id.prorate and prorate and x.factor_percent > 0
        ):
            record.factor = record.get_prorrate_ratio(**prorate)
        super(
            AccountTaxRepartitionLine,
            self.filtered(
                lambda x: not x.tax_id.prorate or not prorate or x.factor_percent <= 0
            ),
        )._compute_factor()

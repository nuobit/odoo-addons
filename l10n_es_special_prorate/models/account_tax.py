# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import account_tax_mixin


class AccountTax(models.Model):
    _inherit = "account.tax"

    prorate = fields.Boolean(string="Prorate")

    @api.constrains(
        "prorate",
        "amount_type",
        "type_tax_use",
        "invoice_repartition_line_ids",
        "refund_repartition_line_ids",
    )
    def _check_prorate(self):
        account_tax_mixin.check_prorate(self)

    def get_non_deductible_percent(self, date, company_id, is_refund):
        value = 0
        repartition_field = (
            is_refund
            and "refund_repartition_line_ids"
            or "invoice_repartition_line_ids"
        )
        for rec in self.filtered("prorate").flatten_taxes_hierarchy():
            account_tax_mixin.check_prorate(rec)
            non_deductible_rep_line = rec.mapped(repartition_field).filtered(
                lambda x: x.repartition_type == "tax"
                and x.factor_percent > 0
                and not x.account_id
            )
            if not non_deductible_rep_line:
                raise ValidationError(
                    _(
                        "On prorate taxes there should be at least "
                        "one repartition line without account"
                    )
                )
            elif len(non_deductible_rep_line) > 1:
                raise ValidationError(
                    _(
                        "On prorate taxes there should be only "
                        "one repartition line without account"
                    )
                )
            value += (
                rec.amount
                * non_deductible_rep_line.with_context(
                    prorate={"date": date, "company_id": company_id}
                ).factor
            )
        return value

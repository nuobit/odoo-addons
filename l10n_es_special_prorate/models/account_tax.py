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
        repartition_field = (
            is_refund
            and "refund_repartition_line_ids"
            or "invoice_repartition_line_ids"
        )
        value = 0
        for rec in self:
            if rec.amount_type == "percent":
                non_deductible_rep_line = rec.mapped(repartition_field).filtered(
                    lambda x: x.repartition_type == "tax"
                    and x.factor_percent > 0
                    and not x.account_id
                )
                if non_deductible_rep_line:
                    if len(non_deductible_rep_line) > 1:
                        raise ValidationError(
                            _(
                                "On non deductible taxes there should be only "
                                "one repartition line without account"
                            )
                        )
                    context = {}
                    if rec.prorate:
                        context = dict(prorate={"date": date, "company_id": company_id})
                    value += (
                        rec.amount
                        * non_deductible_rep_line.with_context(**context).factor
                    )
            elif rec.amount_type == "group":
                for tax_child in rec.children_tax_ids:
                    value += tax_child.get_non_deductible_percent(
                        date, company_id, is_refund
                    )
            else:
                raise NotImplementedError(
                    "Tax type '%s' not suported yet" % rec.amount_type
                )
        return value

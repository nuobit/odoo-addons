# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def get_non_deductible_percent(self, date, company_id, is_refund):
        value = super(AccountTax, self).get_non_deductible_percent(
            date, company_id, is_refund
        )
        for rec in self.filtered(lambda tax: not tax.prorate):
            if rec.amount_type == "percent":
                if not rec.invoice_repartition_line_ids.filtered("account_id"):
                    value += rec.amount

            elif rec.amount_type == "group":
                for tax_child in rec.children_tax_ids:
                    value += tax_child.get_non_deductible_percent(date, company_id)
            else:
                raise NotImplementedError(
                    "Tax type '%s' not suported yet" % rec.amount_type
                )

        return value

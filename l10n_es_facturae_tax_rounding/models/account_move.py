# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_facturae_tax_info(self):
        self.ensure_one()
        output_taxes, withheld_taxes = super()._get_facturae_tax_info()
        if self.company_id.tax_calculation_rounding_method == "round_globally":
            for taxes in (output_taxes, withheld_taxes):
                for tax, values in taxes.items():
                    values["amount"] = tax.get_tax_amount(
                        values["base"], self.currency_id, self.company_id
                    )
        return output_taxes, withheld_taxes


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_facturae_tax_line_info(self, tax):
        self.ensure_one()
        tax_line_info = {}
        sum_tax_amount = 0.0

        for line in self.move_id.line_ids.filtered(
            lambda x: not x.display_type and not x.exclude_from_invoice_tab
        ):
            for line_tax in line.tax_ids.filtered(lambda t: t == tax and t.amount >= 0):
                tax_amount = tax.get_tax_amount(
                    line.price_subtotal, self.currency_id, self.company_id
                )
                tax_line_info.setdefault((line, line_tax), tax_amount)
                sum_tax_amount += tax_amount

        move_tax_line = self.move_id.line_ids.filtered(lambda x: x.tax_line_id == tax)
        total_tax_line_tax_amount = self.currency_id.round(
            sum(move_tax_line.mapped("balance"))
        )
        diff_tax_amount = self.currency_id.round(sum_tax_amount) - (
            -total_tax_line_tax_amount
        )

        if diff_tax_amount != 0:
            sorted_lines = sorted(tax_line_info.keys(), key=lambda k: k[0].id)
            num_lines_to_adjust = min(
                len(sorted_lines), int(abs(diff_tax_amount * 100))
            )
            adjustment_value = 0.01 if diff_tax_amount > 0 else -0.01
            for i in range(num_lines_to_adjust):
                line, line_tax = sorted_lines[i]
                tax_line_info[(line, line_tax)] += adjustment_value

        return tax_line_info[(self, tax)]

# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


def prorate_context(invoice):
    return {
        "date": invoice.date or fields.Date.context_today(invoice),
        "company_id": invoice.company_id.id,
    }


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_tax_lines(
        self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None
    ):
        self = self.with_context(prorate=prorate_context(self))
        return super(AccountMove, self)._recompute_tax_lines(
            recompute_tax_base_amount=recompute_tax_base_amount,
            tax_rep_lines_to_recompute=tax_rep_lines_to_recompute,
        )

    @api.onchange("invoice_date", "date")
    def _onchange_dates(self):
        self._recompute_dynamic_lines()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_price_total_and_subtotal_model(
        self,
        price_unit,
        quantity,
        discount,
        currency,
        product,
        partner,
        taxes,
        move_type,
    ):
        if taxes and self.move_id:
            taxes = taxes.with_context(prorate=prorate_context(self.move_id))
        return super()._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )

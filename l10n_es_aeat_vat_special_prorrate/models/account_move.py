# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_tax_lines(
        self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None
    ):
        self = self.with_context(
            **self.env["account.tax"].prorate_context(self, self.date, self.company_id)
        )
        return super()._recompute_tax_lines(
            recompute_tax_base_amount=recompute_tax_base_amount,
            tax_rep_lines_to_recompute=tax_rep_lines_to_recompute,
        )

    @api.onchange("date")
    def _onchange_dates(self):
        self._recompute_dynamic_lines(
            recompute_all_taxes=True, recompute_tax_base_amount=True
        )


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
            taxes = taxes.with_context(
                **self.env["account.tax"].prorate_context(
                    self.move_id, self.move_id.date, self.move_id.company_id
                )
            )
        if not currency:
            currency = self.currency_id or self.move_id.currency_id
        return super()._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )

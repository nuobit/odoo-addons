# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        vals.update(
            {
                "purchase_value": aml._get_asset_base_value(),
            }
        )
        return vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_asset_base_value(self):
        self.ensure_one()
        value = self.balance
        tax_non_deductible_percent = self.tax_ids.get_non_deductible_percent(
            self.move_id.date or self.move_id.invoice_date,
            self.move_id.company_id.id or self.env.company.id,
            self.move_id.move_type in ("out_refund", "in_refund"),
        )
        if tax_non_deductible_percent:
            value += round(
                value * tax_non_deductible_percent / 100,
                self.currency_id.decimal_places,
            )
        return value

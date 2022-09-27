# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)

        vals.update(
            {
                "invoice_number": self.name,
                "invoice_date": self.invoice_date,
                "tax_base_amount": aml.balance,
            }
        )
        return vals

    def action_post(self):
        super(AccountMove, self.with_context(allow_empty_taxes=True)).action_post()
        for move in self:
            for aml in move.line_ids.filtered(
                lambda line: line.asset_id and not line.tax_line_id
            ):
                aml.with_context(
                    allow_asset=True, allow_asset_removal=True
                ).asset_id.tax_ids = aml.tax_ids

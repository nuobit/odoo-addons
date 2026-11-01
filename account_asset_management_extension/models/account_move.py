# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import Command, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        vals.update(
            {
                "invoice_ref": self.ref,
                "invoice_date": self.invoice_date,
                "quantity": aml.quantity,
                "tax_base_amount": aml.balance,
                "tax_ids": [Command.set(aml.tax_ids.ids)],
            }
        )
        return vals

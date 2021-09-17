# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        if self.date and self.date != self.invoice_date:
            vals.update(
                {
                    "date": self.date,
                }
            )
        return vals

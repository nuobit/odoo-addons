# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import json

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        vals.update(
            {
                "invoice_ref": self.ref,
                "invoice_date": self.invoice_date,
                "tax_base_amount": aml.balance,
                "json_tax_ids": json.dumps(aml.tax_ids.ids),
            }
        )
        return vals

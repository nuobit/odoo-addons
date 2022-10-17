# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountAssetTransfer(models.TransientModel):
    _inherit = "account.asset.transfer"

    def _get_move_line_from_asset(self, asset):
        res = super()._get_move_line_from_asset(asset)
        if asset.account_move_line_ids:
            asset.account_move_line_ids.ensure_one()
            move_line = asset.account_move_line_ids[0]
            res.update(
                {
                    "debit": -asset.purchase_value if move_line.balance < 0 else 0.0,
                    "credit": asset.purchase_value if move_line.balance >= 0 else 0.0,
                }
            )
        else:
            if asset.purchase_value and asset.purchase_value < 0:
                res.update({"debit": -asset.purchase_value, "credit": 0.0})
        return res

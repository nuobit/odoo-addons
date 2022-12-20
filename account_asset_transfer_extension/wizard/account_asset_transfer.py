# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountAssetTransfer(models.TransientModel):
    _inherit = "account.asset.transfer"

    def transfer(self):
        res = super().transfer()
        move = self.env["account.move"].browse(res["domain"][0][2])
        for line in move.line_ids:
            if line.asset_id in self.from_asset_ids:
                line.asset_id.write(
                    {
                        "transfer_move_id": move,
                        "state": "transferred",
                        "date_remove": False,
                        "date_transfer": self.date_transfer,
                    }
                )
        return res

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

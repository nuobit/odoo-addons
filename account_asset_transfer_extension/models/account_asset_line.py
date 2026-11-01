# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    def unlink_move(self):
        for line in self:
            if line.move_id:
                transferred_assets = self.env["account.asset"].search(
                    [("transfer_move_id", "=", line.move_id.id)], limit=1
                )
                if transferred_assets:
                    raise UserError(
                        _(
                            "You cannot unpost this entry because it is a "
                            "transfer move (%s) linked to transferred assets."
                            " Use the 'Revert Transfer' action instead."
                        )
                        % line.move_id.display_name
                    )
        return super().unlink_move()

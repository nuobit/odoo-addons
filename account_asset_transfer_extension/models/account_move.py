# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_exists_asset_transfers(self):
        if not self.env.context.get("force_delete", False):
            for rec in self:
                if rec.line_ids.asset_id.mapped("transfer_move_id"):
                    raise ValidationError(
                        _(
                            "You can't modify or delete a journal item "
                            "on journal entries with transferred assets"
                        )
                    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        self.move_id._check_exists_asset_transfers()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        self.env["account.move"].browse(
            [x["move_id"] for x in vals_list]
        )._check_exists_asset_transfers()
        return super().create(vals_list)

    def unlink(self):
        self.move_id._check_exists_asset_transfers()
        return super().unlink()

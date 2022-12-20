# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountAssetTransfer(models.TransientModel):
    _name = "account.asset.transfer.revert"
    _description = "Revert Transferred Asset"

    warning_message = fields.Text(readonly=True)

    def _get_to_asset_ids(self):
        active_model = self.env.context.get("active_model")
        if not active_model:
            raise ValidationError(_("Active Model not defined"))
        from_asset_ids = self.env.context.get("active_ids", [])
        if not from_asset_ids:
            raise UserError(_("No assets selected"))
        from_assets = self.env[active_model].browse(from_asset_ids)
        return from_assets.mapped("to_asset_ids")

    def _generate_warning_message(self):
        self.ensure_one()
        to_asset_moves = self._group_assets_by_move(self._get_to_asset_ids())
        if not to_asset_moves:
            self.warning_message = _("Nothing to revert")
        else:
            message_l = [_("The next actions will be taken: ")]
            moves = self.env["account.move"].browse(
                map(lambda x: x.id, to_asset_moves.keys())
            )
            message_l.append(
                _("> Journal entries to remove: %s") % ", ".join(moves.mapped("name"))
            )
            to_assets = self.env["account.asset"]
            for assets in to_asset_moves.values():
                to_assets |= assets[1]
            if to_assets:
                message_l.append(
                    _("> New assets to remove: %s")
                    % ", ".join(to_assets.mapped("name"))
                )
            from_assets = self.env["account.asset"]
            for assets in to_asset_moves.values():
                from_assets |= assets[0]
            if from_assets:
                message_l.append(
                    _("> Transferred assets to restore: %s")
                    % ", ".join(from_assets.mapped("name"))
                )
            if message_l:
                self.warning_message = "\n\n".join(message_l)

    def _group_assets_by_move(self, to_assets):
        to_asset_moves = {}
        for asset in to_assets:
            dps = asset.depreciation_line_ids.filtered(lambda x: x.init_entry)
            if len(dps) != 1:
                raise ValidationError(
                    _("Unexpected number of init entries found on deprecation line")
                )
            move = dps[0].move_id
            if move:
                if move in to_asset_moves:
                    to_asset_moves[move][1] |= asset
                else:
                    to_asset_moves[move] = [asset.from_asset_ids, asset]
        return to_asset_moves

    def revert_transfer(self):
        to_assets = self._get_to_asset_ids()
        if not to_assets:
            raise ValidationError(_("Nothing to revert"))
        to_asset_moves = self._group_assets_by_move(to_assets)
        for move, (from_assets, to_assets) in to_asset_moves.items():
            lines_wo_assets = move.line_ids.filtered(lambda x: not x.asset_id)
            if lines_wo_assets:
                raise ValidationError(
                    _("The journal entry %s has lines without asset") % move.name
                )
            if set(move.line_ids.asset_id.ids) != set((from_assets | to_assets).ids):
                raise ValidationError(
                    _(
                        "The journal entry assets has inconsistencies with de from/to assets"
                    )
                )
            move.button_draft()
            move.with_context(force_delete=True).unlink()
            to_assets.set_to_draft()
            to_assets.unlink()
            from_assets.state = "open"

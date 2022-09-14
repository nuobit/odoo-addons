from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMoveAssetReviewWizard(models.TransientModel):
    _name = "account.move.asset.review.wizard"
    _description = "Review current move line assigned asset"

    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="account.asset",
    )

    def _get_depreciation_init_entry(self, asset):
        init_entry = asset.depreciation_line_ids.filtered(lambda x: x.init_entry)
        if not init_entry:
            raise ValidationError(_("No init depreciation line found"))
        if len(init_entry) > 1:
            raise ValidationError(_("More than one init entry found"))
        return init_entry

    def _remove_moveline_asset_profile(self, move_line):
        # Odoo does not allow to remove using the ORM and
        # there's no context key to skip the check
        self.env.cr.execute(
            "update account_move_line set asset_profile_id = null where id = %s",
            (move_line.id,),
        )

    def _update_asset_invoice_link(self, asset, move_line):
        if not move_line:
            move_line = self.env["account.move.line"].browse()
        if asset.move_line_id != move_line:
            asset.move_line_id = move_line
        if asset.move_id != move_line.move_id:
            asset.move_id = move_line.move_id
        init_entry = self._get_depreciation_init_entry(asset)
        if init_entry.move_id != move_line.move_id:
            if not move_line:
                init_entry = init_entry.with_context(unlink_from_asset=True)
            init_entry.move_id = move_line.move_id

    def do_action(self):
        active_model = self.env.context.get("active_model")
        if not active_model:
            raise ValidationError(_("The active model must be set by the caller view"))
        if active_model != "account.move.line":
            raise ValidationError(_("Unexpected active model %s") % active_model)
        active_id = self.env.context.get("active_id")
        if not active_id:
            raise ValidationError(_("The active ID must be set by the caller view"))
        MoveLine = self.env[active_model]
        move_line = MoveLine.browse(
            active_id
        )  # .with_context(allow_asset_removal=True)
        if not move_line:
            raise ValidationError(_("There's no move lines with id %i") % move_line.id)

        if self.asset_id:
            others = MoveLine.search(
                [
                    ("asset_id", "=", self.asset_id.id),
                    ("id", "!=", move_line.id),
                ]
            ).filtered(lambda x: x.move_id.is_purchase_document())
            if others:
                others_msg = [
                    "* {%i} [%s] - {%i} %s"
                    % (x.move_id.id, x.move_id.name, x.id, x.name)
                    for x in others
                ]
                raise ValidationError(
                    _(
                        "Already exists another movements with same asset:\n%s.\n"
                        "Please, remove first the asset from the other movement"
                    )
                    % ("\n".join(others_msg))
                )
            # update asset
            self._update_asset_invoice_link(self.asset_id, move_line)
            # update moveline (asset profile updated automatically)
            if move_line.asset_id != self.asset_id:
                if move_line.asset_id:
                    self._update_asset_invoice_link(move_line.asset_id, False)
                move_line.with_context(
                    allow_asset_removal=True, allow_asset=True
                ).asset_id = self.asset_id
        else:
            if move_line.asset_id:
                # update asset
                self._update_asset_invoice_link(move_line.asset_id, False)
                # update moveline (asset profile not updated if we remove the asset)
                if move_line.asset_profile_id:
                    self._remove_moveline_asset_profile(move_line)
                move_line.with_context(allow_asset_removal=True).asset_id = False

# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    from_asset_ids = fields.Many2many(
        string="From Assets",
        comodel_name="account.asset",
        compute="_compute_from_asset_ids",
    )

    def _compute_from_asset_ids(self):
        for rec in self:
            move_lines = rec.account_move_line_ids.filtered(
                lambda x: x.move_id != rec.transfer_move_id
            )
            move = move_lines.move_id.filtered(
                lambda x: x in x.line_ids.asset_id.transfer_move_id
            )
            if len(move) > 1:
                raise ValidationError(
                    _("More than one move with the same to_asset found")
                )
            rec.from_asset_ids = move.line_ids.asset_id.filtered(
                lambda x: x.transfer_move_id == move
            )

    to_asset_ids = fields.Many2many(
        string="To Assets",
        comodel_name="account.asset",
        compute="_compute_to_asset_ids",
    )

    def _compute_to_asset_ids(self):
        for rec in self:
            if rec.transfer_move_id:
                rec.to_asset_ids = rec.transfer_move_id.line_ids.asset_id.filtered(
                    lambda x: not x.transfer_move_id
                    or x.transfer_move_id != rec.transfer_move_id
                )
            else:
                rec.to_asset_ids = False

    state = fields.Selection(
        selection_add=[("transferred", "Transferred")],
        ondelete={"transferred": "cascade"},
    )
    date_transfer = fields.Date(
        string="Asset Transfer Date",
        readonly=True,
    )
    transfer_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Transfer Move id",
        readonly=True,
    )

    def revert_transfer(self):
        wizard = self.env["account.asset.transfer.revert"].create({})
        wizard._generate_warning_message()
        ctx = dict(self.env.context, active_ids=self.ids)
        res = {
            "name": _("Revert Transfer AUC to Asset"),
            "view_mode": "form",
            "res_model": "account.asset.transfer.revert",
            "target": "new",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "context": ctx,
        }
        return res

    @api.constrains("state", "to_asset_ids")
    def _check_state_to_asset_ids(self):
        for rec in self:
            if rec.to_asset_ids and rec.state != "transferred":
                raise ValidationError(
                    _(
                        "When asset has to_asset_ids, state must be transferred. "
                        "Please, review asset: %s"
                    )
                    % rec.name
                )

    @api.constrains("state", "from_asset_ids")
    def _check_state_from_asset_ids(self):
        for rec in self:
            if rec.from_asset_ids and rec.state not in ["open", "close", "removed"]:
                raise ValidationError(
                    _(
                        "When asset has from_asset_ids, state must be open, close or removed. "
                        "Please, review asset: %s"
                    )
                    % rec.name
                )

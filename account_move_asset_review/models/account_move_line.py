# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _user_review_asset_allowed(self):
        return self.user_has_groups(
            "account_move_asset_review.group_review_move_asset_fields"
        )

    allow_review_asset = fields.Boolean(compute="_compute_allow_review_asset")

    def _compute_allow_review_asset(self):
        for rec in self:
            rec.allow_review_asset = rec._user_review_asset_allowed()

    def action_review_asset(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_move_asset_review.account_move_asset_review_wizard_action"
        )
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx["active_id"] = self.id
        ctx["active_model"] = self._name
        ctx["default_asset_id"] = self.asset_id.id
        action["context"] = ctx
        return action

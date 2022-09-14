# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    @api.model
    def _user_review_asset_allowed(self):
        return self.user_has_groups(
            "account_move_asset_review.group_review_move_asset_fields"
        )

    allow_review_asset = fields.Boolean(compute="_compute_allow_review_asset")

    def _compute_allow_review_asset(self):
        for rec in self:
            rec.allow_review_asset = rec._user_review_asset_allowed()

    def name_get(self):
        res = super().name_get()
        if not self._user_review_asset_allowed():
            return res
        new_res = []
        for _id, name in res:
            new_res.append((_id, "{%s} %s" % (_id, name)))
        return new_res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if not self._user_review_asset_allowed():
            return res
        asset_ids = [x[0] for x in res]
        if name and name.isdigit():
            asset_ids += self.search([("id", "=ilike", name + "%")]).ids
        assets = self.search([("id", "in", asset_ids)], limit=limit)
        return assets.name_get()

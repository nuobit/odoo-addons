# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    allow_update_partner = fields.Boolean(compute="_compute_allow_update_partner")

    def _compute_allow_update_partner(self):
        for rec in self:
            rec.allow_update_partner = self.env.user.has_group(
                "base_user_update_partner.group_user_update_partner"
            )

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    @api.depends("groups_id")
    def _compute_share(self):
        res = super()._compute_share()
        internal_users = self.filtered_domain([("groups_id.is_internal", "=", True)])
        internal_users.share = False
        return res

    @api.model
    def has_group(self, group_ext_id):
        has_group = super().has_group(group_ext_id)
        if group_ext_id == "base.group_user":
            has_group |= bool(self.groups_id.filtered(lambda x: x.is_internal))
        return has_group

    def _is_internal(self):
        res = super()._is_internal()
        if self.sudo().groups_id.filtered(lambda x: x.is_internal):
            res = True
        return res

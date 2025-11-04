# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation == "write" and self.user_has_groups(
            "base_user_partner_fields_edit.group_user_partner_fields_edit"
        ):
            if self.env.context.get("partner_only_fields"):
                return True
        return super().check_access_rights(operation, raise_exception=raise_exception)

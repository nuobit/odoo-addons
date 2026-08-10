# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Users(models.Model):
    _inherit = "res.users"

    def _check_access(self, operation):
        if operation == "write" and self.env.user.has_group(
            "base_user_partner_fields_edit.group_user_partner_fields_edit"
        ):
            if self.env.context.get("partner_only_fields"):
                return None
        return super()._check_access(operation)

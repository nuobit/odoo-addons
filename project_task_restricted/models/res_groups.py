# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    @api.onchange("users")
    def _onchange_users_restricted(self):
        """Before users leave the Restricted tasks group on its form, warn
        how many marked tasks they will be taken off. The form's users are new
        records wrapping the real ones, hence their `_origin`."""
        group = self.env.ref("project_task_restricted.group_restricted_task")
        leavers = (
            self._origin.users - self.users._origin
            if self._origin == group
            else self.env["res.users"]
        )
        warning = self.env["project.task"]._restricted_leave_warning(leavers)
        return {"warning": warning} if warning is not None else {}

    def write(self, vals):
        """Take the users who leave the Restricted tasks group off its marked
        tasks. Only a write of that group's members can make anyone leave it.
        On the module's first install Odoo writes the group's first members
        before the group has its external id: nobody can leave it then."""
        group = self.env.ref(
            "project_task_restricted.group_restricted_task", raise_if_not_found=False
        )
        if "users" not in vals or group is None or group not in self:
            return super().write(vals)
        with self.env["project.task"]._restricted_leavers_removed():
            return super().write(vals)

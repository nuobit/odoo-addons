# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    def write(self, vals):
        """Archiving or restoring a project does it on its tasks, but Odoo
        reaches only those the user can read: the marked ones follow their
        project too."""
        res = super().write(vals)
        if "active" in vals:
            self._restricted_tasks().write({"active": vals["active"]})
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_restricted_tasks(self):
        """Odoo refuses to delete a project with tasks, but counts only those
        the user can read: a project whose tasks are all marked looks empty
        to whoever is outside the group."""
        if self._restricted_tasks():
            raise UserError(
                _(
                    "You cannot delete a project that contains restricted "
                    "tasks. You can archive it instead."
                )
            )

    def _restricted_tasks(self):
        """The marked tasks of these projects, archived ones included. They
        are searched for as superuser: the projects' task list, in memory,
        may hold only the tasks the user can read."""
        return (
            self.env["project.task"]
            .sudo()
            .with_context(active_test=False)
            .search([("project_id", "in", self.ids), ("restricted", "=", True)])
        )

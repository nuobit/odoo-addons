# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTaskStagePersonal(models.Model):
    _inherit = "project.task.stage.personal"

    @api.constrains("task_id", "user_id")
    def _check_restricted_task_user(self):
        """A personal stage is a row of the table of its task's assignees, so
        its user follows the assignees' rule. The rows themselves are checked:
        written through this model, they are not in the database yet when
        constraints run, so the task's assignees do not show them."""
        members = self.env["project.task"]._restricted_members()
        for stage in self.sudo():
            task = stage.task_id._filter_restricted()
            if task and stage.user_id not in members:
                raise task._restricted_assignee_error(stage.user_id)

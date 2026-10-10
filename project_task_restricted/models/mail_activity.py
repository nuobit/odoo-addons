# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.constrains("user_id", "res_model_id", "res_id")
    def _check_restricted_task_user(self):
        """An activity on a marked task follows its task's rule, also the
        automated ones, which Odoo does not check against the document. Only
        the activity written is checked: the task's other activities are not
        this write's concern."""
        Task = self.env["project.task"]
        members = Task._restricted_members()
        for activity in self:
            task = Task._restricted_task_of(activity.res_model, activity.res_id)
            if task and activity.user_id not in members:
                raise task._restricted_activity_error(activity.user_id)

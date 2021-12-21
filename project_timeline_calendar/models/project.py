# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models


class Task(models.Model):
    _inherit = "project.task"

    @api.constrains("date_start", "date_start", "user_id", "project_id")
    def check_ovelap(self):
        for task in self:
            overlaped_tasks = self.search(
                [
                    ("id", "!=", task.id),
                    ("project_id", "=", task.project_id.id),
                    ("user_id", "=", task.user_id.id),
                    ("date_start", "!=", False),
                    ("date_end", "!=", False),
                    ("date_end", ">", task.date_start),
                    ("date_start", "<", task.date_end),
                ],
                limit=1,
            )
            if overlaped_tasks:
                raise ValueError(
                    _("The task would be overlaped with the task %s")
                    % overlaped_tasks[0].name
                )

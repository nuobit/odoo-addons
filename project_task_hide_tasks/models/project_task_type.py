# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    hide_tasks_in_calendar = fields.Boolean(string="Hide Tasks In Calendar")

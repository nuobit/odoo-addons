from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    hide_tasks_in_calendar = fields.Boolean(string="Hide Tasks In Calendar")

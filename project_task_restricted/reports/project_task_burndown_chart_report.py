# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTaskBurndownChartReport(models.Model):
    _inherit = "project.task.burndown.chart.report"

    # the report's view already selects each row's task; its restricted-task
    # rule needs that column as a field
    task_id = fields.Many2one(comodel_name="project.task", readonly=True)

# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    default_timeline_view = fields.Boolean(string="Default timeline view")

    def action_view_tasks(self):
        action = super(Project, self).action_view_tasks()
        if self.default_timeline_view:
            action[
                "view_mode"
            ] = "timeline,kanban,tree,form,calendar,pivot,graph,activity"
            action["views"] = [
                (False, "timeline"),
                (False, "kanban"),
                (False, "tree"),
                (False, "form"),
                (False, "calendar"),
                (False, "pivot"),
                (False, "graph"),
                (False, "activity"),
            ]
        return action

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    default_timeline_view = fields.Boolean(
        string="Default timeline view"
    )

    @api.multi
    def action_project_task(self):
        action = super(Project, self).open_tasks()
        if self.default_timeline_view:
            action['view_mode'] = 'timeline,kanban,tree,form,calendar,pivot,graph,activity'
            action['views'] = [(False, 'timeline'), (False, 'kanban'), (False, 'tree'), (False, 'form'),
                               (False, 'calendar'), (False, 'pivot'), (False, 'graph'), (False, 'activity')]
        return action

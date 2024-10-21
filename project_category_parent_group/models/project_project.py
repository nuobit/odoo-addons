# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    parent_type_id = fields.Many2one(
        comodel_name="project.type",
        string="Parent Type",
        copy=False,
        domain="[('project_ok', '=', True)]",
        compute="_compute_parent_type_id",
        store=True,
    )

    @api.depends("type_id", "type_id.parent_id")
    def _compute_parent_type_id(self):
        for project in self:
            project.parent_type_id = project.type_id.parent_id

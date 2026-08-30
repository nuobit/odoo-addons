# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    lm_date = fields.Date(string="Date")
    lm_employee_ids = fields.Many2many(string="Employees", comodel_name="hr.employee")
    lm_expedient_number = fields.Char(string="Expedient Number")
    lm_issue_ids = fields.Many2many(string="Issues", comodel_name="lm.issue")
    lm_resolution_id = fields.Many2one(
        string="Resolution", comodel_name="lm.resolution"
    )
    lm_amount = fields.Float(string="Amount")
    lm_probability_id = fields.Many2one(
        string="Probability", comodel_name="lm.probability"
    )
    # This field is not necessary on version 15 and above
    lm_issues_complete_name = fields.Char(
        compute="_compute_lm_issues_complete_name",
        store=True,
    )

    @api.depends("lm_issue_ids")
    def _compute_lm_issues_complete_name(self):
        for rec in self:
            rec.lm_issues_complete_name = ", ".join(
                issue.complete_name for issue in rec.lm_issue_ids
            )

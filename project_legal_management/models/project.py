# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    lm_date = fields.Date(string="Date")
    lm_employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employees")
    lm_expedient_number = fields.Char(string="Expedient Number")
    lm_issue_ids = fields.Many2many(comodel_name="lm.issue", string="Issues")
    lm_resolution_id = fields.Many2one(comodel_name="lm.resolution", string="Resolution")
    lm_amount = fields.Float(string="Amount")
    lm_probability_id = fields.Many2one(comodel_name="lm.probability", string="Probability")





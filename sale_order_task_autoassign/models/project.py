# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    department_ids = fields.Many2many(
        comodel_name="hr.department", string="Departments"
    )

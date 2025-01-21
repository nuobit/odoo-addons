# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class HrCourse(models.Model):
    _inherit = "hr.course"

    duration = fields.Float(string="Duration", help="Duration in hours")

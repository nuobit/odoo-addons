# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    bike_location = fields.Selection(
        related="sale_line_id.order_id.bike_location", readonly=True
    )

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Location(models.Model):
    _inherit = "stock.picking"

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="stock_picking_hr_employee_rel",
        column1="picking_id",
        column2="employee_id",
        string="Employees",
    )

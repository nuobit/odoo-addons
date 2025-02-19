# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo import api, fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        ondelete="restrict",
        domain="['|',('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    employee_assigned_date = fields.Datetime(
        readonly=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("employee_id"):
            vals["employee_assigned_date"] = datetime.now()
        return super().create(vals)

    def write(self, vals):
        if vals.get("employee_id"):
            vals["employee_assigned_date"] = datetime.now()
        return super().write(vals)

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Repair(models.Model):
    _inherit = "mrp.repair"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        required=True,
        ondelete="restrict",
        domain="['|',('company_id', '=', False), ('company_id', '=', company_id)]",
    )

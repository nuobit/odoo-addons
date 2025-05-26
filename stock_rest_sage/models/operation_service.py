# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OperationService(Component):
    _inherit = "operation.service"

    def _update_picking_values(self, picking_values, **kwargs):
        res = super()._update_picking_values(picking_values, **kwargs)

        company_id = self.env.user.company_id.id

        # employees
        employees = None
        if kwargs["employees"]:
            sage_company_id = (
                self.env["sage.backend"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company_id),
                    ]
                )
                .sage_company_id
            )
            employees = (
                self.env["sage.hr.employee"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company_id),
                        ("sage_codigo_empresa", "=", sage_company_id),
                        ("sage_codigo_empleado", "in", kwargs["employees"]),
                    ]
                )
            )
            employee_diff = set(kwargs["employees"]) - set(
                employees.mapped("sage_codigo_empleado")
            )
            if employee_diff:
                raise ValidationError(_("Employees %s are not found" % employee_diff))

        if employees:
            res.update(
                {
                    "employee_ids": [(6, False, employees.mapped("odoo_id.id"))],
                }
            )
        return res

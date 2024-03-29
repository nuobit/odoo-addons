# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    sage_bind_ids = fields.One2many(
        comodel_name="sage.hr.employee",
        inverse_name="odoo_id",
        string="Sage Bindings",
    )


class HrEmployeeBinding(models.Model):
    _name = "sage.hr.employee"
    _inherit = "sage.binding"
    _inherits = {"hr.employee": "odoo_id"}
    _description = "Hr employee binding"

    odoo_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=True, ondelete="cascade"
    )

    # composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(sage_codigo_empresa, sage_codigo_empleado)",
            "Empllyee with same ID on Sage already exists.",
        ),
    ]

    def import_employees_since(self, backend_record=None, since_date=None):
        """Prepare the import of employees modified on Sage"""
        filters = {
            "CodigoEmpresa": backend_record.sage_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env["sage.hr.employee"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_employees_since_date = now_fmt

        return True

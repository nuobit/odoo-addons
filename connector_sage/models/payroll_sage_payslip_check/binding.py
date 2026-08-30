# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PayslipCheck(models.Model):
    _inherit = "payroll.sage.payslip.check"

    sage_bind_ids = fields.One2many(
        comodel_name="sage.payroll.sage.payslip.check",
        inverse_name="odoo_id",
        string="Sage Bindings",
    )


class PayslipCheckBinding(models.Model):
    _name = "sage.payroll.sage.payslip.check"
    _inherit = "sage.binding"
    _inherits = {"payroll.sage.payslip.check": "odoo_id"}
    _description = "Payroll sage payslip check binding"

    odoo_id = fields.Many2one(
        comodel_name="payroll.sage.payslip.check",
        string="Payslip check",
        required=True,
        ondelete="cascade",
    )

    # composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado", required=True)

    sage_ano = fields.Integer(string="Año", required=True)
    sage_mesd = fields.Integer(string="MesD", required=True)
    sage_tipo_proceso = fields.Char(string="TipoProceso", required=True)

    sage_id_empleado = fields.Char(string="IdEmpleado", required=True)
    sage_orden_nom = fields.Integer(string="OrdenNom", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(sage_codigo_empresa, sage_codigo_empleado, sage_ano, "
            "sage_mesd, sage_tipo_proceso, sage_id_empleado, sage_orden_nom)",
            "Payroll structure with same ID on Sage already exists.",
        ),
    ]

    def import_payslip_checks(self, payslip_id, backend_record):
        """Prepare the import of payslip from Sage"""
        filters = {
            "CodigoEmpresa": backend_record.sage_company_id,
            "Año": payslip_id.year,
            "MesD": ("between", (payslip_id.month_from, payslip_id.month_to)),
            "TipoProceso": payslip_id.process_id.name,
        }

        self.env["sage.payroll.sage.payslip.check"].import_batch(
            backend=backend_record, filters=filters
        )

        return True

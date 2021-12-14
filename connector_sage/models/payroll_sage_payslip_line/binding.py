# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PayslipLine(models.Model):
    _inherit = "payroll.sage.payslip.line"

    payslip_type = fields.Selection(related="payslip_id.type")

    sage_payroll_bind_ids = fields.One2many(
        comodel_name="sage.payroll.sage.payslip.line.payroll",
        inverse_name="odoo_id",
        string="Sage Payroll Bindings",
    )

    sage_transfer_bind_ids = fields.One2many(
        comodel_name="sage.payroll.sage.payslip.line.transfer",
        inverse_name="odoo_id",
        string="Sage Transfer Bindings",
    )


class PayslipLineBinding(models.AbstractModel):
    _name = "sage.payroll.sage.payslip.line"
    _inherit = "sage.binding"
    _inherits = {"payroll.sage.payslip.line": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="payroll.sage.payslip.line",
        string="Payslip line",
        required=True,
        ondelete="cascade",
    )

    ## composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_convenio = fields.Integer(string="CodigoConvenio", required=True)
    sage_fecha_registro_cv = fields.Date(string="FechaRegistroCV", required=True)

    sage_ano = fields.Integer(string="Año", required=True)
    sage_mesd = fields.Integer(string="MesD", required=True)
    sage_tipo_proceso = fields.Char(string="TipoProceso", required=True)

    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado", required=True)
    sage_codigo_concepto_nom = fields.Integer(string="CodigoConceptoNom", required=True)

    def import_payslip_lines(self, payslip_id, backend_record):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError

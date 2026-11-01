# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PayslipLineTransferBinding(models.Model):
    _name = "sage.payroll.sage.payslip.line.transfer"
    _inherit = "sage.payroll.sage.payslip.line"
    _description = "Payroll sage payslip line transfer binding"

    # composed id
    sage_fecha_cobro = fields.Date(string="FechaCobro", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(sage_codigo_empresa, sage_codigo_convenio, sage_fecha_registro_cv, "
            "sage_ano, sage_mesd, sage_tipo_proceso, "
            "sage_codigo_empleado, sage_codigo_concepto_nom, sage_fecha_cobro)",
            "Transfer Payslip with same ID on Sage already exists.",
        ),
    ]

    def import_payslip_lines(self, payslip_id, backend_record):
        """Prepare the import of payslip from Sage"""
        filters = {
            "CodigoEmpresa": backend_record.sage_company_id,
            "CodigoConvenio": payslip_id.labour_agreement_id.code,
            "FechaRegistroCV": payslip_id.labour_agreement_id.registration_date_cv,
            "Año": payslip_id.year,
            "MesD": ("between", (payslip_id.month_from, payslip_id.month_to)),
            "TipoProceso": payslip_id.process_id.name,
        }
        if payslip_id.payment_date:
            filters["FechaCobro"] = payslip_id.payment_date
        self.env["sage.payroll.sage.payslip.line.transfer"].import_batch(
            backend=backend_record, filters=filters
        )

        return True

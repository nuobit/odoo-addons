# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PayrollSagePayslipProcess(models.Model):
    _inherit = "payroll.sage.payslip.process"

    sage_bind_ids = fields.One2many(
        comodel_name="sage.payroll.sage.payslip.process",
        inverse_name="odoo_id",
        string="Sage Bindings",
    )


class PayrollSagePayslipProcessBinding(models.Model):
    _name = "sage.payroll.sage.payslip.process"
    _inherit = "sage.binding"
    _inherits = {"payroll.sage.payslip.process": "odoo_id"}
    _description = "Payslip process binding"

    odoo_id = fields.Many2one(
        comodel_name="payroll.sage.payslip.process",
        string="Payslip process",
        required=True,
        ondelete="cascade",
    )

    # composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_tipo_proceso = fields.Char(string="TipoProceso", required=True)

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, sage_codigo_empresa, sage_tipo_proceso)",
            "Payslip process with same ID on Sage already exists.",
        ),
    ]

    def import_payslip_processes_since(self, backend_record=None, since_date=None):
        """Prepare the import of payslip processes modified on Sage"""
        filters = {
            "CodigoEmpresa": backend_record.sage_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env["sage.payroll.sage.payslip.process"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_payslip_processes_since_date = now_fmt

        return True

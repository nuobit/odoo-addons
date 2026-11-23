# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
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

    def _get_payslip_filters(self, payslip_id, backend_record):
        """The filter of the payslip's transfer lines in Sage. The payslip's
        checks follow its lines, so the same filter selects them too."""
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
        return filters

    def import_payslip_lines(self, payslip_id, backend_record):
        """Prepare the import of payslip from Sage"""
        self.env["sage.payroll.sage.payslip.line.transfer"].import_batch(
            backend=backend_record,
            filters=self._get_payslip_filters(payslip_id, backend_record),
            payslip=payslip_id,
        )

        return True

    def import_payslip_lines_and_checks(self, payslip_id, backend_record):
        """Import the lines and the checks of a transfer payslip in one job.
        Both are decided before either is written, so a refusal of the lines
        or of the checks writes neither."""
        filters = self._get_payslip_filters(payslip_id, backend_record)
        with backend_record.work_on(
            "sage.payroll.sage.payslip.line.transfer", payslip=payslip_id
        ) as line_work, backend_record.work_on(
            "sage.payroll.sage.payslip.check", payslip=payslip_id
        ) as check_work:
            line_importer = line_work.component(usage="batch.importer")
            check_importer = check_work.component(usage="batch.importer")
            line_plan = line_importer._plan(filters)
            check_plan = check_importer._plan(filters)
            line_importer._apply(line_plan)
            check_importer._apply(check_plan)

        return True

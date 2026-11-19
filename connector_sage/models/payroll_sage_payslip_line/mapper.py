# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping, only_create


class PayslipLineImportMapper(AbstractComponent):
    _name = "sage.payroll.sage.payslip.line.import.mapper"
    _inherit = "sage.import.mapper"

    direct = [
        ("ImporteNom", "amount"),
        ("ConceptoLargo", "name"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("CodigoConvenio", "sage_codigo_convenio"),
        ("FechaRegistroCV", "sage_fecha_registro_cv"),
        ("Año", "sage_ano"),
        ("MesD", "sage_mesd"),
        ("TipoProceso", "sage_tipo_proceso"),
        ("CodigoConceptoNom", "sage_codigo_concepto_nom"),
        ("CodigoEmpleado", "sage_codigo_empleado"),
    ]

    @mapping
    def wage_type_line_id(self, record):
        external_id = [
            record["CodigoEmpresa"],
            record["CodigoConvenio"],
            record["FechaRegistroCV"],
            record["CodigoConceptoNom"],
        ]

        binder = self.binder_for("sage.payroll.sage.labour.agreement.wage.type.line")
        wage_type_line = binder.to_internal(external_id, unwrap=True)

        assert wage_type_line, (
            f"wage_type_line_id {external_id} should have been imported in "
            "PayrollSageLabourAgreementImporter._import_dependencies"
        )

        return {"wage_type_line_id": wage_type_line.id}

    @mapping
    def employee_id(self, record):
        external_id = [record["CodigoEmpresa"], record["CodigoEmpleado"]]

        binder = self.binder_for("sage.hr.employee")
        employee = binder.to_internal(external_id, unwrap=True)

        assert employee, (
            f"employee_id {external_id} should have been imported in "
            "HrEmployeeImporter._import_dependencies"
        )

        return {"employee_id": employee.id}

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def payslip_id(self, record):
        payslip = self.work.payslip
        if payslip is None or not payslip.exists():
            raise UserError(
                _(
                    "This job has no destination payslip, because it was queued "
                    "without one or because its payslip was deleted. Cancel the "
                    "job and, if the payslip still exists, import it again."
                )
            )
        payslip.ensure_one()
        return {"payslip_id": payslip.id}

# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class PayslipCheckImportMapper(Component):
    _name = "sage.payroll.sage.payslip.check.import.mapper"
    _inherit = "sage.import.mapper"

    _apply_on = "sage.payroll.sage.payslip.check"

    direct = [
        ("Importe", "amount"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("Año", "sage_ano"),
        ("MesD", "sage_mesd"),
        ("TipoProceso", "sage_tipo_proceso"),
        ("CodigoEmpleado", "sage_codigo_empleado"),
        ("IdEmpleado", "sage_id_empleado"),
        ("OrdenNom", "sage_orden_nom"),
    ]

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

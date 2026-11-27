# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipLineDelayedBatchImporter(Component):
    """Import the Sage Employees.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.payroll.sage.payslip.line.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"
    _apply_on = [
        "sage.payroll.sage.payslip.line.payroll",
        "sage.payroll.sage.payslip.line.transfer",
    ]

    def run(self, filters=None):
        """Run the synchronization"""
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, external_id, job_options=None):
        """Delay the import of the record into the payslip of this import"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, payslip=self.work.payslip
        )


class PayslipLineImporter(Component):
    _name = "sage.payroll.sage.payslip.line.importer"
    _inherit = "sage.importer"
    _apply_on = [
        "sage.payroll.sage.payslip.line.payroll",
        "sage.payroll.sage.payslip.line.transfer",
    ]

    def _import_dependencies(self):
        external_id = (
            self.external_data["CodigoEmpresa"],
            self.external_data["CodigoEmpleado"],
        )

        self._import_dependency(external_id, "sage.hr.employee", always=False)

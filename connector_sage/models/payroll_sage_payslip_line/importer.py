# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
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

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipCheckDelayedBatchImporter(Component):
    """Import the Sage Employees.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.payroll.sage.payslip.check.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"

    _apply_on = "sage.payroll.sage.payslip.check"

    def run(self, filters=None):
        """ Run the synchronization """
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)


class PayslipCheckImporter(Component):
    _name = "sage.payroll.sage.payslip.check.importer"
    _inherit = "sage.importer"
    _apply_on = "sage.payroll.sage.payslip.check"

    def _import_dependencies(self):
        external_id = (
            self.external_data["CodigoEmpresa"],
            self.external_data["CodigoEmpleado"],
        )

        self._import_dependency(external_id, "sage.hr.employee", always=False)

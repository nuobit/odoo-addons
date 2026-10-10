# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayrollSagePayslipProcessBatchImporter(Component):
    """Import the Sage Payslip Processes.

    For every payslip process in the list, a delayed job is created.
    """

    _name = "sage.payroll.sage.payslip.process.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"
    _apply_on = "sage.payroll.sage.payslip.process"


class PayrollSagePayslipProcessImporter(Component):
    _name = "sage.payroll.sage.payslip.process.importer"
    _inherit = "sage.importer"
    _apply_on = "sage.payroll.sage.payslip.process"

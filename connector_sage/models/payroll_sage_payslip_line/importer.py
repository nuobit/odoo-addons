# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipLineDelayedBatchImporter(Component):
    """Import the Sage Employees.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.payroll.sage.payslip.line.delayed.batch.importer"
    _inherit = "sage.payslip.delayed.batch.importer"
    _apply_on = [
        "sage.payroll.sage.payslip.line.payroll",
        "sage.payroll.sage.payslip.line.transfer",
    ]


class PayslipLineImporter(Component):
    _name = "sage.payroll.sage.payslip.line.importer"
    _inherit = "sage.payslip.importer"
    _apply_on = [
        "sage.payroll.sage.payslip.line.payroll",
        "sage.payroll.sage.payslip.line.transfer",
    ]

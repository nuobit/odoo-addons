# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipCheckDelayedBatchImporter(Component):
    """Import the Sage Employees.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.payroll.sage.payslip.check.delayed.batch.importer"
    _inherit = "sage.payslip.delayed.batch.importer"

    _apply_on = "sage.payroll.sage.payslip.check"


class PayslipCheckImporter(Component):
    _name = "sage.payroll.sage.payslip.check.importer"
    _inherit = "sage.payslip.importer"
    _apply_on = "sage.payroll.sage.payslip.check"

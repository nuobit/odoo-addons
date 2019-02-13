# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component


class PayslipLinePayrollImportMapper(Component):
    _name = 'sage.payroll.sage.payslip.line.payroll.import.mapper'
    _inherit = 'sage.payroll.sage.payslip.line.import.mapper'

    _apply_on = 'sage.payroll.sage.payslip.line.payroll'

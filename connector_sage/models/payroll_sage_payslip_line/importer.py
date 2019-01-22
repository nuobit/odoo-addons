# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class PayslipLineBatchImporter(Component):
    """ Import the Sage Employees.

    For every partner in the list, a delayed job is created.
    """
    _name = 'sage.payroll.sage.payslip.line.delayed.batch.importer'
    _inherit = 'sage.delayed.batch.importer'
    _apply_on = 'sage.payroll.sage.payslip.line'


class PayslipLineImporter(Component):
    _name = 'sage.payroll.sage.payslip.line.importer'
    _inherit = 'sage.importer'
    _apply_on = 'sage.payroll.sage.payslip.line'

    # def _import_dependencies(self):
    #     external_id = (self.external_data['CodigoEmpresa'], self.external_data['CodigoEmpleado'])
    #
    #     self._import_dependency(external_id, 'sage.res.partner', always=True)

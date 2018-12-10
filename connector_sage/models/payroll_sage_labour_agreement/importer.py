# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class PayrollSageLabourAgreementBatchImporter(Component):
    """ Import the Sage Payroll Structure.

    For every payroll structure in the list, a delayed job is created.
    """
    _name = 'sage.payroll.sage.labour.agreement.batch.importer'
    _inherit = 'sage.delayed.batch.importer'
    _apply_on = 'sage.payroll.sage.labour.agreement'


class PayrollSageLabourAgreementImporter(Component):
    _name = 'sage.payroll.sage.labour.agreement.importer'
    _inherit = 'sage.importer'
    _apply_on = 'sage.payroll.sage.labour.agreement'

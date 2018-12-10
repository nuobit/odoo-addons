# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ResPartnerBatchImporter(Component):
    """ Import the Sage Partners.

    For every partner in the list, a delayed job is created.
    """
    _name = 'sage.res.partner.batch.importer'
    _inherit = 'sage.delayed.batch.importer'
    _apply_on = 'sage.res.partner'


class ResPartnerImporter(Component):
    _name = 'sage.res.partner.importer'
    _inherit = 'sage.importer'
    _apply_on = 'sage.res.partner'

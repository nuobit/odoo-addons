# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ResPartnerBatchImporter(Component):
    """ Import the Ambugest Partners.

    For every partner in the list, a delayed job is created.
    """
    _name = 'ambugest.res.partner.delayed.batch.importer'
    _inherit = 'ambugest.delayed.batch.importer'
    _apply_on = 'ambugest.res.partner'


class ResPartnerImporter(Component):
    _name = 'ambugest.res.partner.importer'
    _inherit = 'ambugest.importer'
    _apply_on = 'ambugest.res.partner'

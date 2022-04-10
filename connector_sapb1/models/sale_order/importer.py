# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """ Import the Sap B1 Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'sapb1.sale.order.delayed.batch.importer'
    _inherit = 'sapb1.delayed.batch.importer'

    _apply_on = 'sapb1.sale.order'


class SaleOrderImporter(Component):
    _name = 'sapb1.sale.order.importer'
    _inherit = 'sapb1.importer'

    _apply_on = 'sapb1.sale.order'

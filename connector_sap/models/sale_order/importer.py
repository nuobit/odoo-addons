# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """ Import the Sap Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'sap.sale.order.delayed.batch.importer'
    _inherit = 'sap.delayed.batch.importer'

    _apply_on = 'sap.sale.order'


class SaleOrderImporter(Component):
    _name = 'sap.sale.order.importer'
    _inherit = 'sap.importer'

    _apply_on = 'sap.sale.order'

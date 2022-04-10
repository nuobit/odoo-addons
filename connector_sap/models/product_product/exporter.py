# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class ProductProductDelayedBatchImporter(Component):
    """ Import the SAPB1 Product.

    For every partner in the list, a delayed job is created.
    """
    _name = 'sap.product.product.delayed.batch.exporter'
    _inherit = 'sap.delayed.batch.exporter'

    _apply_on = 'sap.product.product'


class ProductProductDirectBatchImporter(Component):
    """ Import the SAPB1 Partners.

    For every partner in the list, import it directly.
    """
    _name = 'sap.product.product.direct.batch.exporter'
    _inherit = 'sap.direct.batch.exporter'

    _apply_on = 'sap.product.product'


class ProductProductImporter(Component):
    _name = 'sap.product.product.exporter'
    _inherit = 'sap.exporter'

    _apply_on = 'sap.product.product'



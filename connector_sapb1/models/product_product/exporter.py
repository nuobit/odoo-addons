# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class ProductProductDelayedBatchImporter(Component):
    """ Import the SAP B1 Product.

    For every product in the list, a delayed job is created.
    """
    _name = 'sapb1.product.product.delayed.batch.exporter'
    _inherit = 'sapb1.delayed.batch.exporter'

    _apply_on = 'sapb1.product.product'


class ProductProductDirectBatchImporter(Component):
    """ Import the SAP B1 Products.

    For every partner in the list, import it directly.
    """
    _name = 'sapb1.product.product.direct.batch.exporter'
    _inherit = 'sapb1.direct.batch.exporter'

    _apply_on = 'sapb1.product.product'


class ProductProductImporter(Component):
    _name = 'sapb1.product.product.exporter'
    _inherit = 'sapb1.exporter'

    _apply_on = 'sapb1.product.product'



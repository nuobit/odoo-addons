# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import (IDMissingInBackend,
                                             RetryableJobError)


class ProductProductBatchExporter(Component):
    """ Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """
    _name = 'oxigesti.product.product.delayed.batch.exporter'
    _inherit = 'oxigesti.delayed.batch.exporter'
    _apply_on = 'oxigesti.product.product'


class ProductProductExporter(Component):
    _name = 'oxigesti.product.product.exporter'
    _inherit = 'oxigesti.exporter'
    _apply_on = 'oxigesti.product.product'

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ProductProductImportMapper(Component):
    _name = 'sapb1.product.product.export.mapper'
    _inherit = 'sapb1.export.mapper'

    _apply_on = 'sapb1.product.product'

    direct = [('default_code', 'ItemCode'),('sapb1_sku', 'SKU')]

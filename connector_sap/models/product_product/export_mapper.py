# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ProductProductImportMapper(Component):
    _name = 'sap.product.product.export.mapper'
    _inherit = 'sap.export.mapper'

    _apply_on = 'sap.product.product'

    direct = [('default_code', 'ItemCode'),('sap_sku', 'SKU')]

    # @mapping
    # def backend_id(self, record):
    #     return {'backend_id': self.backend_record.id}

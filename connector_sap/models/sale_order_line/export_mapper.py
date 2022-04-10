# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)


class SaleOrderLineImportMapper(Component):
    _name = 'sap.sale.order.line.export.mapper'
    _inherit = 'sap.export.mapper'

    _apply_on = 'sap.sale.order.line'

    direct = [
        ('product_uom_qty', 'Quantity'),
        ('price_unit', 'UnitPrice'),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def product(self, record):
        return {'ItemCode': record.product_id.code}

    @mapping
    def linenum(self,record):
        return{'LineNum':2,'DocEntry':160666}

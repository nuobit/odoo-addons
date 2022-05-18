# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderLineImportMapper(Component):
    _name = 'lengow.sale.order.line.import.mapper'
    _inherit = 'lengow.import.mapper'

    _apply_on = 'lengow.sale.order.line'

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def lengow_line_id(self, record):
        binder = self.binder_for()
        external_id = binder.dict2id(record, in_field=False)
        return binder.id2dict(external_id, in_field=True)

    @mapping
    def price_unit(self, record):
        if record['quantity']:
            return {'price_unit': (float(record['amount']) - float(record['tax'])) / record['quantity']}
        binding = self.options.get("binding")
        if not binding:
            return {'price_unit': (float(record['amount']) - float(record['tax']))}

    @mapping
    def product(self, record):
        external_id = record['sku']
        binder = self.binder_for('lengow.product.product')
        product_odoo = binder.to_internal(external_id, unwrap=True)
        assert product_odoo, (
                "product_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % (external_id,))
        return {'product_id': product_odoo.id}

    @mapping
    def quantity(self, record):
        if not record['quantity'] == 0:
            return {'product_uom_qty': record['quantity']}
        else:
            binding = self.options.get("binding")
            if not binding:
                return {'product_uom_qty': record['quantity']}

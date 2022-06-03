# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderImportMapChild(Component):
    _name = 'veloconnect.sale.order.map.child.import'
    _inherit = 'veloconnect.map.child.import'

    _apply_on = 'veloconnect.sale.order.line'

    def get_item_values(self, map_record, to_attr, options):
        binder = self.binder_for('veloconnect.sale.order.line')
        external_id = binder.dict2id(map_record.source, in_field=False)
        veloconnect_order_line = binder.to_internal(external_id, unwrap=False)
        if veloconnect_order_line:
            map_record.update(id=veloconnect_order_line.id)
        return map_record.values(**options)

    def format_items(self, items_values):
        ops = []
        for values in items_values:
            id = values.pop('id', None)
            if id:
                ops.append((1, id, values))
            else:
                ops.append((0, False, values))
        return ops


class SaleOrderImportMapper(Component):
    _name = 'veloconnect.sale.order.import.mapper'
    _inherit = 'veloconnect.import.mapper'

    _apply_on = 'veloconnect.sale.order'

    direct = [('phone_home', 'phone'),
              ('email', 'email')]

    children = [('items', 'veloconnect_order_line_ids', 'veloconnect.sale.order.line')]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}


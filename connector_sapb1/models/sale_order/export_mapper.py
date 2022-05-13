# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderExportMapChild(Component):
    _name = 'sapb1.sale.order.map.child.export'
    _inherit = 'sapb1.map.child.export'

    _apply_on = 'sapb1.sale.order.line'

    def get_item_values(self, map_record, to_attr, options):
        return super().get_item_values(map_record, to_attr, options)

    def format_items(self, items_values):
        return super().format_items(items_values)


class SaleOrderExportMapper(Component):
    _name = 'sapb1.sale.order.export.mapper'
    _inherit = 'sapb1.export.mapper'

    _apply_on = 'sapb1.sale.order'

    direct = [
        ('client_order_ref', 'NumAtCard'),
    ]

    children = [('order_line', 'DocumentLines', 'sapb1.sale.order.line')]

    @mapping
    def partner(self, record):
        parent = record.partner_shipping_id.parent_id
        if not parent:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == record.partner_shipping_id)
            # to_delete
            # raise ValidationError(_('No parent partner found for partner %s') % record.name)
        else:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == parent)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for parent %s') % parent.name)
        return {'CardCode': partner_map.sapb1_cardcode}

    @only_create
    @mapping
    def date(self, record):
        date = fields.Date.from_string(record.date_order)
        # to_active
        # return {'DocDueDate': date, 'DocDate': date, 'TaxDate': date}

        # return {'DocDueDate': date, 'TaxDate': date}
        return {'DocDueDate': date}

    @mapping
    def shiptocode(self, record):
        binder = self.binder_for('sapb1.res.partner')
        binding = binder.wrap_record(record.partner_shipping_id)
        assert binding, (
                "partner %s should have been exported in "
                "SaleOrderExporter._export_dependencies" % record.partner_shipping_id)
        return {'ShipToCode': binding.sapb1_addressname}

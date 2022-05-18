# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create, changed_by)
from odoo.exceptions import ValidationError


class SaleOrderExportMapChild(Component):
    _name = 'sapb1.sale.order.map.child.export'
    _inherit = 'sapb1.map.child.export'

    _apply_on = 'sapb1.sale.order.line'

    def get_item_values(self, map_record, to_attr, options):
        return super().get_item_values(map_record, to_attr, options)

    def format_items(self, items_values):
        return super().format_items(items_values)

    def skip_item(self, map_record):
        return map_record.source.product_id == self.backend_record.shipping_product_id


class SaleOrderExportMapper(Component):
    _name = 'sapb1.sale.order.export.mapper'
    _inherit = 'sapb1.export.mapper'

    _apply_on = 'sapb1.sale.order'

    direct = [
        ('client_order_ref', 'NumAtCard'),
    ]

    children = [('order_line', 'DocumentLines', 'sapb1.sale.order.line')]

    @changed_by('partner_id')
    @mapping
    def partner(self, record):
        parent = record.partner_shipping_id.parent_id
        if not parent:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == record.partner_shipping_id)
        else:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == parent)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for parent %s') % parent.name)
        return {'CardCode': partner_map.sapb1_cardcode}

    @only_create
    @mapping
    def date(self, record):
        date = fields.Date.from_string(record.date_order)
        return {'DocDueDate': date, 'DocDate': date, 'TaxDate': date}

    @mapping
    def shiptocode(self, record):
        binder = self.binder_for('sapb1.res.partner')
        binding = binder.wrap_record(record.partner_shipping_id)
        assert binding, (
                "partner %s should have been exported in "
                "SaleOrderExporter._export_dependencies" % record.partner_shipping_id)
        return {'ShipToCode': binding.sapb1_addressname}

    @mapping
    def shipping(self, record):
        expenses = {"DocumentAdditionalExpenses": []}
        shipping_line = record.order_line.filtered(lambda x: self.backend_record.shipping_product_id == x.product_id)
        if len(shipping_line) > 1:
            raise ValidationError(_('Only one shipping line supported'))
        if not shipping_line:
            return expenses
        partner = record.partner_id.parent_id or record.partner_id
        partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == partner)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for %s. Please define it on backend') % partner.name)
        expensecode = partner_map.sapb1_expensecode
        if not expensecode:
            raise ValidationError(
                _('No expense code defined for partner %s. Please define it on backend') % partner.name)
        expense = {
            'ExpenseCode': expensecode,
            'LineTotal': shipping_line.get_raw_price_unit(),
        }
        if shipping_line.tax_id:
            expense['VatGroup'] = self.backend_record.get_tax_map(shipping_line.tax_id)
        expenses['DocumentAdditionalExpenses'].append(expense)
        return expenses

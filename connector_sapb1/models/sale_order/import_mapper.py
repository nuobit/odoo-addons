# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderImportMapChild(Component):
    _name = 'sapb1.sale.order.map.child.import'
    _inherit = 'sapb1.map.child.import'

    _apply_on = 'sapb1.sale.order.line'

    def get_item_values(self, map_record, to_attr, options):
        binder = self.binder_for('sapb1.sale.order.line')
        external_id = map_record.source['id']
        sapb1_order_line = binder.to_internal(external_id, unwrap=False)
        if sapb1_order_line:
            map_record.update(id=sapb1_order_line.id)
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
    _name = 'sapb1.sale.order.import.mapper'
    _inherit = 'sapb1.import.mapper'

    _apply_on = 'sapb1.sale.order'

    direct = [('phone_home', 'phone'),
              ('email', 'email')]

    children = [('items', 'sapb1_order_line_ids', 'sapb1.sale.order.line')]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}

    @mapping
    def delivery_address(self, record):
        binder = self.binder_for('sapb1.res.partner')
        external_id = binder.dict2id(record['delivery_address'],in_field=False)
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
                "partner_shipping_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id)
        return {'partner_shipping_id': partner.id}

    @mapping
    def billing_address(self, record):
        binder = self.binder_for('sapb1.res.partner')
        external_id = binder.dict2id(record['billing_address'],in_field=False)
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
                "partner_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % external_id)
        if not partner.active:
            raise ValidationError(_("The partner %s, with id:%s is archived, please, enable it") %
                                  (partner.name, partner.id))
        partner_return = {'partner_invoice_id': partner.id}
        if partner.parent_id:
            partner_return['partner_id'] = partner.parent_id.id
        else:
            partner_return['partner_id'] = partner.id
        return partner_return

    @only_create
    @mapping
    def order_date(self, record):
        return {
            'date_order': record['marketplace_order_date'],
            'confirmation_date': record['marketplace_order_date'],
            'validity_date': record['marketplace_order_date'],
        }

    @only_create
    @mapping
    def team_id(self, record):
        return {'team_id': None}

    @only_create
    @mapping
    def user_id(self, record):
        return {'user_id': None}


    @mapping
    def marketplace_status(self, record):
        return {'marketplace_status': record['marketplace_status']}

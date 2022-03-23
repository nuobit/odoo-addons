# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """ Import the Lengow Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'lengow.sale.order.delayed.batch.importer'
    _inherit = 'lengow.delayed.batch.importer'

    _apply_on = 'lengow.sale.order'


class SaleOrderImporter(Component):
    _name = 'lengow.sale.order.importer'
    _inherit = 'lengow.importer'

    _apply_on = 'lengow.sale.order'

    def _import_dependencies(self, external_data):
        # Customer
        billing_address = external_data['billing_address']
        binder = self.binder_for('lengow.res.partner')
        self._import_dependency(binder.dict2id(billing_address, in_field=False), 'lengow.res.partner',
                                external_data=billing_address,
                                always=False)
        delivery_address = external_data['delivery_address']
        self._import_dependency(binder.dict2id(delivery_address, in_field=False), 'lengow.res.partner',
                                external_data=delivery_address,
                                always=False)
        # Products
        order_lines = external_data['items']
        for line in order_lines:
            self._import_dependency(line['sku'], 'lengow.product.product',
                                    external_data={'sku': line['sku']},
                                    always=False)

    def _after_import(self, binding):
        # We search if the email of our billing address already has a partner with parent id = null
        # If it has one but not of the 'invoice' type, we reassign all its children and this same partner
        # to the new billing address.
        # If it has one of the 'invoice' type, we assign it, and if not we put parent_id=Null
        # For shipping address, we check if there is a partner with the same email and assign it as parent_id
        # Finally, we confirm order

        potential_parent = self.env['res.partner'].search([
            ("email", "=", binding.partner_invoice_id.email),
            ("parent_id", "=", False),
            ("id", "!=", binding.partner_invoice_id.id),
        ])
        if len(potential_parent) > 1:
            raise ValidationError(_("Expecting 1 potential parent, %s found") % len(potential_parent))
        if potential_parent and potential_parent.type != 'invoice':
            binding.partner_invoice_id.parent_id = False
            potential_parent.parent_id = binding.partner_invoice_id.id

            childs = self.env['res.partner'].search([
                ("parent_id", "=", potential_parent.id)
            ])
            childs.write({
                'parent_id': binding.partner_invoice_id.id
            })
        elif potential_parent:
            binding.partner_invoice_id.parent_id = potential_parent.id
        else:
            binding.partner_invoice_id.parent_id = False

        potential_parent = self.env['res.partner'].search([
            ("email", "=", binding.partner_shipping_id.email),
            ("parent_id", "=", False),
            ("id", "!=", binding.partner_shipping_id.id)
        ])
        if len(potential_parent) > 1:
            raise ValidationError(_("Expecting 1 potential parent, %s found") % len(potential_parent))
        if potential_parent:
            binding.partner_shipping_id.parent_id = potential_parent.id

        ## order validation
        sale_order = self.binder_for().unwrap_binding(binding)
        sale_order.action_confirm()

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
        parent = self.env['res.partner'].search([('name', '=', binding.lengow_marketplace)])
        if not parent:
            self.env["res.partner"].create(
                {
                    "name": binding.lengow_marketplace
                })
        parent = self.env['res.partner'].search([('name', '=', binding.lengow_marketplace)])
        binding.partner_invoice_id.parent_id = parent.id
        binding.partner_shipping_id.parent_id = parent.id

        ## order validation
        sale_order = self.binder_for().unwrap_binding(binding)
        sale_order.action_confirm()

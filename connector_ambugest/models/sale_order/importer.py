# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class SaleOrderBatchImporter(Component):
    """ Import the Ambugest Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'ambugest.sale.order.delayed.batch.importer'
    _inherit = 'ambugest.delayed.batch.importer'
    _apply_on = 'ambugest.sale.order'


class SaleOrderImporter(Component):
    _name = 'ambugest.sale.order.importer'
    _inherit = 'ambugest.importer'
    _apply_on = 'ambugest.sale.order'

    def _must_skip(self, binding):
        if not binding:
            return None

        order = self.component(usage='binder').unwrap_binding(binding)
        if order.state != 'draft':
            state_option = dict(
                order.fields_get(['state'], ['selection'])
                    .get('state').get('selection'))

            return _('The Order %s is %s -> Update not allowed' % (order.name, state_option[order.state]))

        return None

    def _import_dependencies(self):
        external_id = (self.external_data['EMPRESA'], self.external_data['CodiUP'])

        self._import_dependency(external_id, 'ambugest.res.partner', always=False)

    def _import_finalize(self, binding):
        sale_order = self.component(usage='binder').unwrap_binding(binding)
        sale_order.onchange_partner_id()
        for line in sale_order.order_line:
            line.product_id_change()
        sale_order.action_confirm()
        sale_order.action_done()

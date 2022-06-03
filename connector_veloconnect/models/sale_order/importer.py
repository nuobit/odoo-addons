# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class SaleOrderBatchImporter(Component):
    """ Import the Veloconnect Services.

    For every sale order in the list, a delayed job is created.
    """
    _name = 'veloconnect.sale.order.delayed.batch.importer'
    _inherit = 'veloconnect.delayed.batch.importer'

    _apply_on = 'veloconnect.sale.order'


class SaleOrderImporter(Component):
    _name = 'veloconnect.sale.order.importer'
    _inherit = 'veloconnect.importer'

    _apply_on = 'veloconnect.sale.order'

    def _import_dependencies(self, external_data):
        # Customer
        billing_address = external_data['billing_address']
        binder = self.binder_for('veloconnect.res.partner')
        if billing_address:
            self._import_dependency(binder.dict2id(billing_address, in_field=False), 'veloconnect.res.partner',
                                    external_data=billing_address,
                                    always=False)
        delivery_address = external_data['delivery_address']
        if delivery_address:
            self._import_dependency(binder.dict2id(delivery_address, in_field=False), 'veloconnect.res.partner',
                                    external_data=delivery_address,
                                    always=False)
        # Products
        order_lines = external_data['items']
        for line in order_lines:
            if not line['is_shipping']:
                self._import_dependency(line['sku'], 'veloconnect.product.template',
                                        external_data={'sku': line['sku']},
                                        always=False)

    def _after_import(self, binding):
        sale_order = self.binder_for().unwrap_binding(binding)
        for line in sale_order.order_line:
            line._compute_tax_id()

        ## order cancel
        if binding.veloconnect_status == 'canceled':
            sale_order.action_cancel()
        else:
            ## order validation
            sale_order.action_confirm()

    def _pre_must_skip(self, external_id, external_data, had_external_data):
        if external_data['veloconnect_status'] != 'canceled':
            if not external_data['delivery_address']:
                if not had_external_data:
                    raise RetryableJobError(_("Delivery Address not yet populated. The job will be retried later"))
                self.model.with_delay().import_record(self.backend_record, external_id)
                return _("The data of the order is not complete yet. "
                         "New job created")
        return False

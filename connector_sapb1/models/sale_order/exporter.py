# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

from ...components.adapter import SAPClosedOrderException

_logger = logging.getLogger(__name__)


class SAPB1SaleOrderBatchDirectExporter(Component):
    """Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """

    _name = "sapb1.sale.order.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "sapb1.sale.order"


class SAPB1SaleOrderBatchDelayedExporter(Component):
    """Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """

    _name = "sapb1.sale.order.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "sapb1.sale.order"


class SaleOrderExporter(Component):
    _name = "sapb1.sale.order.record.direct.exporter"
    _inherit = "sapb1.record.direct.exporter"

    _apply_on = "sapb1.sale.order"

    def _export_dependencies(self, relation):
        self._export_dependency(relation.partner_shipping_id, "sapb1.res.partner")
        for line in relation.order_line:
            if line.product_id != self.backend_record.shipping_product_id:
                self._export_dependency(line.product_id, "sapb1.product.product")

    def _after_export(self, binding):
        """Can do several actions after exporting a record on the backend"""
        if binding.state == "cancel":
            self.backend_adapter.cancel(binding.sapb1_docentry)

    def _update(self, external_id, data):
        """Update an External record"""
        try:
            res = super()._update(external_id, data)
        except SAPClosedOrderException as e:
            res = e.name
        return res

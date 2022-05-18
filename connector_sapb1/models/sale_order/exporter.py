# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrderDelayedBatchExporter(Component):
    """ Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """
    _name = "sapb1.sale.order.delayed.batch.exporter"
    _inherit = "sapb1.delayed.batch.exporter"

    _apply_on = "sapb1.sale.order"


class SaleOrderDirectBatchExporter(Component):
    """ Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """
    _name = "sapb1.sale.order.direct.batch.exporter"
    _inherit = "sapb1.direct.batch.exporter"

    _apply_on = "sapb1.sale.order"


class SaleOrderExporter(Component):
    _name = "sapb1.sale.order.exporter"
    _inherit = "sapb1.exporter"

    _apply_on = "sapb1.sale.order"

    def _export_dependencies(self, relation):
        self._export_dependency(relation.partner_shipping_id, "sapb1.res.partner")
        for line in relation.order_line:
            if line.product_id != self.backend_record.shipping_product_id:
                self._export_dependency(line.product_id, "sapb1.product.product")

    def _after_export(self):
        """ Can do several actions after exporting a record on the backend """
        if self.binding.state == 'cancel':
            self.backend_adapter.cancel(self.binding.sapb1_docentry)

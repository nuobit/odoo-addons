# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderDelayedBatchExporter(Component):
    """ Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """
    _name = "sap.sale.order.delayed.batch.exporter"
    _inherit = "sap.delayed.batch.exporter"

    _apply_on = "sap.sale.order"


class SaleOrderDirectBatchExporter(Component):
    """ Export the Odoo Sale Orders.

    For every sale order in the list, a delayed job is created.
    """
    _name = "sap.sale.order.direct.batch.exporter"
    _inherit = "sap.direct.batch.exporter"

    _apply_on = "sap.sale.order"


class SaleOrderExporter(Component):
    _name = "sap.sale.order.exporter"
    _inherit = "sap.exporter"

    _apply_on = "sap.sale.order"

    def _export_dependencies(self,relation):
        # self._export_dependency(relation.partner_id, 'partner_id', 'sap.res.partner')
        self._export_dependency(relation.partner_shipping_id, "sap.res.partner")


        for line in relation.order_line:
            self._export_dependency(line.product_id, "sap.product.product")

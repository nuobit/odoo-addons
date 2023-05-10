# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceSaleOrderExportMapper(Component):
    _name = "woocommerce.sale.order.export.mapper"
    _inherit = "woocommerce.export.mapper"

    _apply_on = "woocommerce.sale.order"

    @mapping
    def status(self, record):
        if record.woocommerce_order_state == "processing":
            status = "on-hold" if record.state == "draft" else "processing"
        elif record.woocommerce_order_state == "done":
            status = "completed"
        else:
            status = "cancelled"
        return {"status": status}

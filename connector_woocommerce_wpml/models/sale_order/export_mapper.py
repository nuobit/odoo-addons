# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceWPMLSaleOrderExportMapper(Component):
    _name = "woocommerce.wpml.sale.order.export.mapper"
    _inherit = "woocommerce.wpml.export.mapper"

    _apply_on = "woocommerce.wpml.sale.order"

    @mapping
    def status(self, record):
        if record.woocommerce_order_state == "processing":
            status = "on-hold" if record.state == "draft" else "processing"
        elif record.woocommerce_order_state == "done":
            status = "completed"
        else:
            status = "cancelled"
        return {"status": status}

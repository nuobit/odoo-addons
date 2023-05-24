# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderLineBinder(Component):
    _name = "woocommerce.sale.order.line.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.sale.order.line"

    external_id = ["id", "order_id"]
    internal_id = [
        "woocommerce_order_line_id",
        "woocommerce_sale_order_id",
    ]

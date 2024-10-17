# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBinder(Component):
    _name = "woocommerce.sale.order.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.sale.order"

    external_id = "id"
    internal_id = "woocommerce_idsaleorder"

    internal_alt_id = "client_order_ref"

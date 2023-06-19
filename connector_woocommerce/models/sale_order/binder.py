# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBinder(Component):
    _name = "woocommerce.sale.order.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.sale.order"

    external_id = "id"
    internal_id = "woocommerce_idsaleorder"

    # external_alt_id = "sku"
    # internal_alt_id = "default_code"

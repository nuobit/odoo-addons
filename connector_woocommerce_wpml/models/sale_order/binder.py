# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLSaleOrderBinder(Component):
    _name = "woocommerce.wpml.sale.order.binder"
    _inherit = "woocommerce.wpml.binder"

    _apply_on = "woocommerce.wpml.sale.order"

    external_id = "id"
    internal_id = "woocommerce_wpml_idsaleorder"

    internal_alt_id = "client_order_ref"

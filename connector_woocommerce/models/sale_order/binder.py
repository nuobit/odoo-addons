# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBinder(Component):
    _name = "woocommerce.sale.order.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.sale.order"

    external_id = "id"
    internal_id = "woocommerce_idsaleorder"

    internal_alt_id = "client_order_ref"
    #
    # def to_internal(self, external_id, unwrap=False):
    #     return (
    #         super()
    #         .to_internal(external_id, unwrap=unwrap)
    #         .with_context(woocommerce_import=True)
    #     )
    #
    # def to_binding_from_external_key(self, internal_data, now_fmt):
    #     return (
    #         super()
    #         .to_binding_from_external_key(internal_data, now_fmt)
    #         .with_context(woocommerce_import=True)
    #     )

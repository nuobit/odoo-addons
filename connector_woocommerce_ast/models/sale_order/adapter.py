# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderAdapter(Component):
    _inherit = "woocommerce.sale.order.adapter"

    def _prepare_meta_data_fields(self):
        meta_data_fields = super()._prepare_meta_data_fields()
        meta_data_fields.append("_wc_shipment_tracking_items")
        return meta_data_fields

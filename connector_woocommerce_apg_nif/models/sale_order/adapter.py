# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderAdapter(Component):
    _inherit = "woocommerce.sale.order.adapter"

    _apply_on = "woocommerce.sale.order"

    def _get_hash_fields(self):
        hash_fields = super()._get_hash_fields()
        return hash_fields + ["nif"]

    def _get_billing(self, value, hash_fields):
        if value.get("billing"):
            for item in value["meta_data"]:
                if item["key"] == "_billing_nif":
                    value["billing"]["nif"] = item["value"]
        super()._get_billing(value, hash_fields)

    def _get_shipping(self, value, hash_fields):
        if value.get("shipping"):
            for item in value["meta_data"]:
                if item["key"] == "_shipping_nif":
                    value["shipping"]["nif"] = item["value"]
        super()._get_shipping(value, hash_fields)

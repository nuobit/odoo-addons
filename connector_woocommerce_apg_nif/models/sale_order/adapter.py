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

    def _get_partner_parent_domain(self, dir_type, value):
        domain = super()._get_partner_parent_domain(dir_type, value)
        if value[dir_type].get("nif"):
            domain.append(("vat", "=", value[dir_type]["nif"]))
        else:
            if (
                dir_type == "shipping"
                and value["shipping"]["name"] == value["billing"]["name"]
            ):
                domain.append(("id", "=", value["billing"]["parent"]))
        return domain

    def _additional_partner_parent_fields(self, value, dir_type):
        return {
            **super()._additional_partner_parent_fields(value, dir_type),
            "vat": value[dir_type].get("nif"),
        }

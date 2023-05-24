# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

from ..common.tools import list2hash


class WooCommerceSaleOrder(Component):
    _name = "woocommerce.sale.order.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.sale.order"

    def get_total_items(self, domain=None):
        return super().get_total_items("orders", domain=domain)

    def search_read(self, domain=None, offset=0, limit=None):
        real_domain, common_domain = self._extract_domain_clauses(
            domain, self._get_filters_values()
        )
        # /orders?after
        res = self._exec("get", "orders", domain=domain)
        self._reorg_order_data(res)
        return res, len(res)

    def _get_partner_parent(self, dir_type, value):
        # TODO: slug for company name?
        parent = self.env["res.partner"].search(
            [
                ("name", "=", value[dir_type]["company"]),
                ("company_type", "=", "company"),
            ]
        )
        if not parent:
            parent = self.env["res.partner"].create(
                {"name": value[dir_type]["company"], "company_type": "company"}
            )
            value[dir_type]["parent"] = parent.id
        elif len(parent) > 1:
            raise ValidationError(
                _("There are more than one partner with the same name")
            )
        else:
            value[dir_type]["parent"] = parent.id

    def _reorg_order_data(self, values):
        # reorganize data
        for value in values:
            hash_fields = [
                "name",
                "address_1",
                "address_2",
                "city",
                "postcode",
                "email",
                "phone",
                "company",
                "state",
                "country",
            ]
            if value.get("billing"):
                value["billing"]["type"] = "billing"
                if value["billing"].get("company"):
                    self._get_partner_parent("billing", value)
                value["billing"]["name"] = (
                    value["billing"]["first_name"] + " " + value["billing"]["last_name"]
                )
                value["billing"]["hash"] = list2hash(
                    value["billing"].get(x) for x in hash_fields
                )
            # TODO: comprobar si el shipping te dades.
            #  si no, no fer el hash. El shipping no té email.
            if value["shipping"].get("first_name") or value["shipping"].get(
                "last_name"
            ):
                if value["shipping"].get("company"):
                    self._get_partner_parent("shipping", value)
                value["shipping"]["type"] = "shipping"
                if value["shipping"].get("first_name"):
                    value["shipping"]["name"] = value["shipping"]["first_name"]
                    if value["shipping"].get("last_name"):
                        value["shipping"]["name"] += (
                            " " + value["shipping"]["last_name"]
                        )
                else:
                    value["shipping"]["name"] = value["shipping"]["last_name"]
                value["shipping"]["hash"] = list2hash(
                    value["shipping"].get(x) for x in hash_fields
                )
            else:
                value["shipping"] = None
            value["items"] = value.pop("line_items")
            value["product"] = value["items"]
            for product in value["product"]:
                if product.get("variation_id"):
                    product["id"] = product["variation_id"]
                    product["parent_id"] = product["product_id"]
                else:
                    product["id"] = product["product_id"]
            for line in value["items"]:
                line["order_id"] = value["id"]

    # TODO: add more allowed filters in api
    def _get_filters_values(self):
        res = super()._get_filters_values()
        res.append("modified_after")
        return res

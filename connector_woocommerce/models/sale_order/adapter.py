# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

from ....connector_extension.common.tools import list2hash


class WooCommerceSaleOrderAdapter(Component):
    _name = "woocommerce.sale.order.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.sale.order"

    def get_total_items(self, resource=None, domain=None):
        return super().get_total_items("orders", domain=domain)

    def read(self, external_id):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "orders/%s" % (external_id_values["id"])
        res = self._exec("get", url, limit=1)
        self._reorg_order_data(res)
        if len(res) > 1:
            raise ValidationError(
                _("More than one order found with the same id: %s")
                % (external_id_values["id"])
            )
        return res[0]

    def search_read(self, domain=None, offset=0, limit=None):
        self._convert_format_domain(domain)
        if limit:
            res = self._exec("get", "orders", domain=domain, offset=offset, limit=limit)
        else:
            res = self._exec("get", "orders", domain=domain, offset=offset)
        self._reorg_order_data(res)
        return res, len(res)

    def write(self, external_id, data):  # pylint: disable=W8106
        self._prepare_data(data)
        url_l = ["orders", str(external_id[0])]
        return self._exec("put", "/".join(url_l), data=data)

    def _prepare_data(self, data):
        meta_data = self.prepare_meta_data(data)
        if meta_data:
            data["meta_data"] = meta_data

    def _get_partner_parent(self, dir_type, value):
        # TODO: REVIEW: slug for company name?
        domain = [
            ("name", "=", value[dir_type]["company"]),
            ("company_type", "=", "company"),
        ]
        if value[dir_type].get("nif"):
            domain.append(("vat", "=", value[dir_type]["nif"]))
        parent = self.env["res.partner"].search(domain)
        if not parent:
            parent = self.env["res.partner"].create(
                {
                    "name": value[dir_type]["company"],
                    "company_type": "company",
                    "vat": value[dir_type].get("nif"),
                }
            )
            value[dir_type]["parent"] = parent.id
        elif len(parent) > 1:
            raise ValidationError(
                _("There are more than one partner with the same name")
            )
        else:
            value[dir_type]["parent"] = parent.id

    def _get_hash_fields(self):
        return [
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

    def _get_billing(self, value, hash_fields):
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

    def _get_shipping(self, value, hash_fields):
        if value.get("shipping"):
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
        else:
            value["shipping"] = None

    def _reorg_order_data(self, values):
        # reorganize data
        for value in values:
            hash_fields = self._get_hash_fields()
            self._get_billing(value, hash_fields)
            self._get_shipping(value, hash_fields)
            if not value.get("products"):
                value["products"] = []
            for item in value["line_items"]:
                item["order_id"] = value["id"]
                item["is_shipping"] = False
                if not float(item["subtotal"]):
                    item["discount"] = 0
                else:
                    item["discount"] = (
                        1 - float(item["total"]) / float(item["subtotal"])
                    ) * 100
                product = {
                    "id": item["variation_id"]
                    if item.get("variation_id")
                    else item["product_id"],
                    "sku": item["sku"],
                    "name": item["name"],
                    "type": "variation" if item.get("variation_id") else "simple",
                }
                if item.get("variation_id"):
                    product["parent_id"] = item["product_id"]
                value["products"].append(product)
            for shipping in value["shipping_lines"]:
                value["line_items"].append(
                    {
                        "order_id": value["id"],
                        "is_shipping": True,
                        "taxes": shipping["taxes"],
                        "total": shipping["total"],
                        "subtotal": shipping["total"],
                        "quantity": 1,
                        "id": shipping["id"],
                        "discount": 0,
                        "total_tax": shipping["total_tax"],
                    }
                )

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res += [
            "status",
            "after",
            "date_created_gmt",
            "modified_after",
            "modified_before",
        ]
        return res

    def _prepare_domain(self, domain):
        self._convert_format_domain(domain)

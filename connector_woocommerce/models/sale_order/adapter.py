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

    # TODO: deberiamos devolver las orders que salen + las que estan trash. El problema es que en el import chunk
    #  no podemos saber como hacer estos chunks, con que orden, ya que los gets deberian ser distintos
    def get_total_items(self, domain=None):
        return super().get_total_items("orders", domain=domain)

    def read(self, external_id):  # pylint: disable=W8106
        external_id = self.binder_for().id2dict(external_id, in_field=False)
        url = "orders/%s" % (external_id["id"])
        res = self._exec("get", url)
        self._reorg_order_data(res)
        return res[0]

    def search_read(self, domain=None, offset=0, limit=None):
        # real_domain, common_domain = self._extract_domain_clauses(
        #     domain, self._get_filters_values()
        # )
        # if offset:
        #     domain += [("offset", "=", offset)]
        # if limit:
        #     domain += [("per_page", "=", limit)]
        res = self._exec("get", "orders", domain=domain, offset=offset, limit=limit)
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
            if not value.get("products"):
                value["products"] = []
            for item in value["line_items"]:
                item["order_id"] = value["id"]
                item["is_shipping"] = False
                item["discount"] = (
                                       1 - float(item["total"]) / float(item["subtotal"])
                                   ) * 100
                if item.get("variation_id"):
                    value["products"].append(
                        {
                            "id": item["variation_id"],
                            "parent_id": item["product_id"],
                            "sku": item["sku"],
                            "type": "variation",
                        }
                    )
                else:
                    value["products"].append(
                        {"id": item["product_id"], "sku": item["sku"], "type": "simple"}
                    )
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

    # TODO: add more allowed filters in api
    def _get_filters_values(self):
        res = super()._get_filters_values()
        res.append("status")
        return res

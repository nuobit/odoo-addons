# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

from ....connector_extension.common.tools import list2hash


class LengowSaleOrderTypeAdapter(Component):
    _name = "lengow.sale.order.adapter"
    _inherit = "connector.lengow.adapter"

    _apply_on = "lengow.sale.order"

    _datetimestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    def _str_to_datetime(self, sdt):
        try:
            return datetime.datetime.strptime(sdt, self._datetimestamp_format)
        except ValueError:
            return datetime.datetime.strptime(sdt, self._datetime_format)

    def _prepare_results(self, result):
        return result

    def read(self, _id):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(_id, in_field=False)
        domain = [(key, "=", value) for key, value in external_id_values.items()]
        res = self.search_read(domain)
        external_values = None
        if res:
            values = res[0]
            if len(values) > 1:
                raise ValidationError(
                    _("Found more than 1 record for an unique key %s") % _id
                )
            external_values = values[0]
        return external_values

    def search_read(self, domain):
        filters_values = [
            "marketplace",
            "marketplace_order_id",
            "merchant_order_id",
            "lengow_status",
            "marketplace_status",
            "marketplace_order_date_from",
            "marketplace_order_date_to",
            "imported_from",
            "imported_to",
            "updated_from",
            "updated_to",
        ]
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        kw_base_params = self._domain_to_normalized_dict(real_domain)
        res = self._exec(
            "orders", **self._prepare_parameters(kw_base_params, [], filters_values)
        )
        self._format_order_data(res)
        res = self._filter(res, common_domain)
        self._reorg_order_data(res)
        return res, len(res)

    def _format_order_data(self, values):
        conv_mapper = {
            "/marketplace_order_date": lambda x: datetime.datetime.strptime(
                x, self._datetime_format
            ),
            "/total_tax": lambda x: float(x),
            "/commission": lambda x: float(x),
            "/original_total_tax": lambda x: float(x),
            "/original_commission": lambda x: float(x),
            "/packages/cart/amount": lambda x: float(x),
            "/packages/cart/tax": lambda x: float(x),
            "/packages/cart/original_amount": lambda x: float(x),
            "/packages/cart/original_tax": lambda x: float(x),
            "/imported_at": self._str_to_datetime,
            "/updated_at": self._str_to_datetime,
        }
        self._convert_format(values, conv_mapper)

    def _reorg_order_data(self, values):
        # reorganize data
        for value in values:
            packages = value["packages"]
            if len(packages) > 1:
                raise ValidationError(_("Multiple delivery addresses not supported"))
            value["items"] = packages[0].pop("cart")
            delivery = packages[0].pop("delivery")
            delivery.pop("trackings")
            value["delivery_address"] = delivery or None
            hash_fields = [
                "complete_name",
                "first_line",
                "second_line",
                "zipcode",
                "city",
                "common_country_iso_a2",
            ]
            fields = ["delivery_address", "billing_address"]
            for f in fields:
                if value[f]:
                    if (
                        not value["delivery_address"]
                        or "common_country_iso_a2" not in value["delivery_address"]
                    ):
                        value[f]["parent_country_iso_a2"] = None
                    else:
                        value[f]["parent_country_iso_a2"] = value["delivery_address"][
                            "common_country_iso_a2"
                        ]
                    value[f]["marketplace"] = value["marketplace"]
                    if not value[f].get("full_name") or "full_name" not in value[f]:
                        name_values = [
                            value[f][y].strip()
                            for y in ["first_name", "last_name"]
                            if value.get(f) and value[f].get(y)
                        ]
                        complete_name = " ".join(name_values) or None
                    else:
                        complete_name = value[f]["full_name"]
                    value[f]["complete_name"] = complete_name
                    value[f]["hash"] = list2hash(value[f].get(x) for x in hash_fields)
            for item in value["items"]:
                item["sku"] = item.pop("merchant_product_id")["id"]
                item["is_shipping"] = False
                item["marketplace"] = value["marketplace"]
                item["marketplace_order_id"] = value["marketplace_order_id"]
            if value["shipping"]:
                value["items"].append(
                    {
                        "is_shipping": True,
                        "amount": value["shipping"],
                        "quantity": 1,
                        "id": -1,
                        "marketplace": value["marketplace"],
                        "marketplace_order_id": value["marketplace_order_id"],
                    }
                )

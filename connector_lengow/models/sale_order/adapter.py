# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo.addons.connector_lengow.models.common.tools import list2hash


class LengowSaleOrderTypeAdapter(Component):
    _name = "lengow.sale.order.adapter"
    _inherit = "lengow.adapter"

    _apply_on = "lengow.sale.order"

    def _prepare_results(self, result):
        return result

    def read(self, _id):
        external_id_values = self.binder_for().id2dict(_id, in_field=False)
        domain = [(key, "=", value) for key, value in external_id_values.items()]
        res = self.search_read(domain)
        if len(res) > 1:
            raise ValidationError(_("Found more than 1 record for an unique key %s") % _id)
        return res[0] or None

    def search_read(self, domain):
        filters_values = ["marketplace", "marketplace_order_id", "merchant_order_id", "lengow_status",
                          "marketplace_status", "marketplace_order_date_from", "marketplace_order_date_to",
                          "imported_from", "imported_to", "updated_from", "updated_to"]
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        kw_base_params = self._domain_to_normalized_dict(real_domain)
        res = self._exec('orders', **self._prepare_parameters(kw_base_params, [], filters_values))
        self._format_order_data(res)
        res = self._filter(res, common_domain)
        self._reorg_order_data(res)
        return res

    def _format_order_data(self, values):
        conv_mapper = {
            "/marketplace_order_date": lambda x: datetime.datetime.strptime(x, self._datetime_format),
            "/total_tax": lambda x: float(x),
            "/commission": lambda x: float(x),
            "/original_total_tax": lambda x: float(x),
            "/original_commission": lambda x: float(x),
            "/packages/cart/amount": lambda x: float(x),
            "/packages/cart/tax": lambda x: float(x),
            "/packages/cart/original_amount": lambda x: float(x),
            "/packages/cart/original_tax": lambda x: float(x),
            "/imported_at": lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "/updated_at": lambda x: datetime.datetime.strptime(x, self._datetime_format),
        }
        self._convert_format(values, conv_mapper)

    def _reorg_order_data(self, values):
        # reorganize data
        for value in values:
            packages = value['packages']
            if len(packages) > 1:
                raise ValidationError(_("Multiple delivery addresses not supported"))
            value['items'] = packages[0].pop('cart')
            delivery = packages[0].pop('delivery')
            delivery.pop('trackings')
            value['delivery_address'] = delivery or None
            if value['delivery_address']:
                value['delivery_address']['marketplace'] = value['marketplace']
            if value['billing_address']:
                value['billing_address']['marketplace'] = value['marketplace']
            hash_fields = ['complete_name', 'first_line', 'second_line', 'zipcode', 'city', 'common_country_iso_a2']
            fields = ['delivery_address', 'billing_address']
            for f in fields:
                if value['marketplace_status'] == 'CANCELED':
                    a = 1
                name_values = [value[f][y] for y in ['first_name', 'last_name'] if value.get(f) and value[f].get(y)]
                if name_values:
                    value[f]['complete_name'] = ' '.join(name_values)
                    value[f]['hash'] = list2hash(
                        value[f].get(x) for x in hash_fields)
            for item in value['items']:
                item['sku'] = item.pop('merchant_product_id')['id']

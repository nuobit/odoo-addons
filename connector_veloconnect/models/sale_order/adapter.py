# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo.addons.connector_veloconnect.models.common.tools import list2hash


class VeloconnectSaleOrderTypeAdapter(Component):
    _name = "veloconnect.sale.order.adapter"
    _inherit = "veloconnect.adapter"

    _apply_on = "veloconnect.sale.order"

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
        filters_values = ["updated_to"]
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
            "/packages/cart/original_tax": lambda x: float(x),
            "/imported_at": lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "/updated_at": lambda x: datetime.datetime.strptime(x, self._datetime_format),
        }
        self._convert_format(values, conv_mapper)

    def _reorg_order_data(self, values):
        # reorganize data
        for value in values:
            packages = value['packages']


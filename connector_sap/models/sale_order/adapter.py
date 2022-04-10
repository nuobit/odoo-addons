# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class SapSaleOrderTypeAdapter(Component):
    _name = "sap.sale.order.adapter"
    _inherit = "sap.adapter"

    _apply_on = "sap.sale.order"

    def _prepare_results(self, result):
        if result['next'] or result['previous']:
            raise ValidationError(_('Order pagination is not supported'))
        return result['results']

    def read(self, _id):
        return True

    def search_read(self, domain):
        raise NotImplementedError

    def _format_order_params(self, values):
        conv_mapper = {
            "/DocDueDate": lambda x: x.strftime(self._date_format),
        }
        self._convert_format(values, conv_mapper)

    def _reorg_order_data(self, values):
        return True

    def create(self, values):
        """ Create a record on the external system """
        self._format_order_params(values)
        return self._exec('create_order', values=values)

    def write(self, external_id, values):
        """ Update records on the external system """
        self._format_order_params(values)
        self._exec('update_order', external_id=external_id, values=values)

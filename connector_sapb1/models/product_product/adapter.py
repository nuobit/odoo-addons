# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo.addons.connector_sapb1.models.common.tools import list2hash


class SapB1ProductProductTypeAdapter(Component):
    _name = "sapb1.product.product.adapter"
    _inherit = "sapb1.adapter"

    _apply_on = "sapb1.product.product"

    def _prepare_results(self, result):
        return True
        # if result['next'] or result['previous']:
        #     raise ValidationError(_('Order pagination is not supported'))
        # return result['results']

    def read(self, external_id):
        result = self._exec('get_product', external_id=external_id, )
        return result

    def search_read(self, domain):
        kw_base_params = self._domain_to_normalized_dict(domain)
        res = self._exec('get_products', values=kw_base_params)
        return res

    def _format_order_params(self, values):
        return True

    def _reorg_order_data(self, values):
        return True

    def create(self, values):
        raise ValidationError(
            _(
                "Create operation is not supported on products by SAP B1. Values: %s. "
                % (values,)
            )
        )

    def write(self, external_id, values):
        """ Update records on the external system """
        raise NotImplementedError

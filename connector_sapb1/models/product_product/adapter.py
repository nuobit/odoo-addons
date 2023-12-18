# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class SapB1ProductProductTypeAdapter(Component):
    _name = "sapb1.product.product.adapter"
    _inherit = "connector.sapb1.adapter"

    _apply_on = "sapb1.product.product"

    def search_read(self, domain):
        kw_base_params = self._domain_to_normalized_dict(domain)
        res = self._exec("get_products", values=kw_base_params)
        return res

    def create(self, values):  # pylint: disable=W8106
        raise ValidationError(
            _(
                "Create operation is not supported on products by SAP B1. Values: %s. "
                % (values,)
            )
        )

    def write(self, external_id, values):  # pylint: disable=W8106
        raise ValidationError(
            _(
                "Write operation is not supported on products by SAP B1. Values: %s. "
                % (values,)
            )
        )

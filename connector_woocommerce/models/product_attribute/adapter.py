# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeAdapter(Component):
    _name = "cwoocommerce.product.attribute.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.attribute"

    def read(self, _id):  # pylint: disable=W8106
        url_l = ["products/attributes", str(_id)]
        return self._exec("get", "/".join(url_l))

    def search_read(self, domain=None):
        return self._exec("get", "products/attributes", domain=domain)

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/attributes", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products/attributes", str(external_id[0])]
        return self._exec("put", "/".join(url_l), data=data)

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.append("slug")
        return res

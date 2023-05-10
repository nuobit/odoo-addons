# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttribute(Component):
    _name = "woocommerce.product.attribute.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.attribute"

    def read(self, _id):  # pylint: disable=W8106
        url_l = ["products/attributes", str(_id)]
        return self._exec("get", "/".join(url_l))

    def search_read(self, filters=None):
        return self._exec("get", "products/attributes", domain=filters)

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/attributes", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products/attributes", str(external_id)]
        return self._exec("put", "/".join(url_l), data=data)

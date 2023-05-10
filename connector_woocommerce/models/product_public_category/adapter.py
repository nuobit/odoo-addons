# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategory(Component):
    _name = "woocommerce.product.public.category.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.public.category"

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/categories", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products/categories", str(external_id)]
        return self._exec("put", "/".join(url_l), data=data)

    def search_read(self, filters=None):
        a=1
        return self._exec("get", "products/categories", domain=filters)
# ?sku="+sku

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryAdapter(Component):
    _name = "woocommerce.product.public.category.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.public.category"

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/categories", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products/categories", str(external_id[0])]
        return self._exec("put", "/".join(url_l), data=data)

    def search_read(self, domain=None):
        return self._exec("get", "products/categories", domain=domain)

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.append("slug")
        return res

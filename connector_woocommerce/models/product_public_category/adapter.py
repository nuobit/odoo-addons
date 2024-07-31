# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryAdapter(Component):
    _name = "woocommerce.product.public.category.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.public.category"

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/categories", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/categories/%s" % external_id_values["id"]
        return self._exec("put", url, data=data)

    def search_read(self, domain=None):
        return self._exec("get", "products/categories", domain=domain)

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.append("slug")
        return res

    def delete(self, external_id):
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/categories/%s" % external_id_values["id"]
        return self._exec("delete", url, params={"force": "1"})

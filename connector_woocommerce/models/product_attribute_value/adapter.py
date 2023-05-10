# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValue(Component):
    _name = "woocommerce.product.attribute.value"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.attribute.value"

    def read(self, external_id):  # pylint: disable=W8106
        url_l = ["products/attributes", str(external_id)]
        return self._exec("get", "/".join(url_l))

    def search_read(self, filters=None):
        id_list = list(self.binder_for().id2dict(_id, in_field=False).items())
        filters = [(key, "=", value) for key, value in id_list]

        return self._exec("get", "products/attributes", domain=filters)

    def create(self, data):  # pylint: disable=W8106
        # TODO: remove this check
        if not "parent_id" in data:
            raise Exception("Parent ID is required for create")
        return self._exec(
            "post", "products/attributes/%s/terms" % data.pop("parent_id"), data=data
        )

    def write(self, external_id, data):  # pylint: disable=W8106
        if not "parent_id" in data:
            raise Exception("Parent ID is required for write")
        url_l = [
            "products/attributes/%s/terms" % data.pop("parent_id"),
            str(external_id),
        ]
        return self._exec("put", "/".join(url_l), data=data)

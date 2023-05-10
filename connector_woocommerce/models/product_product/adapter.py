# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProduct(Component):
    _name = "woocommerce.product.product.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.product"

    # def read(self, _id):  # pylint: disable=W8106
    #     # url_l = ["products/"]
    #     # id_list = list(self.binder_for().id2dict(_id, in_field=False).items())
    #     # filters = [(key, "=", value) for key, value in id_list]
    #
    #     return self._exec("get", "/".join(url_l))

    def create(self, data):  # pylint: disable=W8106
        url_l = ["products"]
        parent = data.pop("parent_id")
        url_l.append("%s/variations" % parent)
        res = self._exec("post", "/".join(url_l), data=data)
        res["product_tmpl_external_id"] = parent
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products"]
        if "parent_id" in data:
            url_l.append("%s/variations" % data.pop("parent_id"))
        url_l.append("%s" % external_id)
        return self._exec("put", "/".join(url_l), data=data)

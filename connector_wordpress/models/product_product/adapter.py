# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressProductProduct(Component):
    _name = "wordpress.product.product.adapter"
    _inherit = "wordpress.adapter"

    _apply_on = "wordpress.product.product"

    def read(self, _id):  # pylint: disable=W8106
        return self._exec("get", "/".join(url_l))

    def create(self, data):  # pylint: disable=W8106
        url_l = ["products"]
        if "parent_id" in data:
            url_l.append("/%s/variations" % data.pop("parent_id"))

        return self._exec("post", "/".join(url_l), data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products"]
        if "parent_id" in data:
            url_l.append("%s/variations" % data.pop("parent_id"))
        url_l.append("%s" % external_id)
        return self._exec("put", "/".join(url_l), data=data)

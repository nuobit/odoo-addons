# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceIrAttachment(Component):
    _name = "woocommerce.ir.attachment.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.ir.attachment"

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = ["products", str(external_id)]
        return self._exec("put", "/".join(url_l), data=data)

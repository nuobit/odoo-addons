# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachment(Component):
    _name = "wordpress.ir.attachment.adapter"
    _inherit = "wordpress.adapter"

    _apply_on = "wordpress.ir.attachment"

    def create(self, data):  # pylint: disable=W8106
        if "alternative_binding_id" in data:
            return {"id": data["alternative_binding_id"]}
        return self._exec("post", "media", data=data)

    # def write(self, external_id, data):  # pylint: disable=W8106
    #     url_l = ["media", str(external_id)]
    #     return self._exec("put", "/".join(url_l), data=data)

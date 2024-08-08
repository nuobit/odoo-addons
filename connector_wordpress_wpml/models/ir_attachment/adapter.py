# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachment(Component):
    _inherit = "wordpress.ir.attachment.adapter"

    # def _get_search_fields(self):
    #     res = super()._get_search_fields()
    #     res.append("lang")
    #     return res

    def create(self, data):  # pylint: disable=W8106
        lang = data.pop("lang")
        res = super().create(data)
        res["lang"] = lang
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        return self._exec("put", "media/%s" % external_id_values["id"], data=data)

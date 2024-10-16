# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrChecksum(Component):
    _inherit = "wordpress.ir.checksum.adapter"

    def create(self, data):  # pylint: disable=W8106
        lang = data.pop("lang")
        res = super().create(data)
        res["lang"] = lang
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        lang = data.pop("lang")
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        res = self._exec("put", "media/%s" % external_id_values["id"], data=data)
        res["lang"] = lang
        return res

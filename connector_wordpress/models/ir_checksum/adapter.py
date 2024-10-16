# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrChecksum(Component):
    _name = "wordpress.ir.checksum.adapter"
    _inherit = "wordpress.adapter"

    _apply_on = "wordpress.ir.checksum"

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "media", data=data)

    def read(self, external_id):  # pylint: disable=W8106
        # TODO: REVIEW: Check external_id_values, external_id and
        #  external_id_values["id] nullability
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        return self._exec("get", "media/%s" % external_id_values["id"])

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, external_id_fields)
        external_id_values = binder.dict2id2dict(domain_dict, in_field=False)
        if external_id_values:
            url = "media/%s" % external_id_values["id"]
        else:
            url = "media"
        return self._exec("get", url, domain=common_domain)

    def write(self, external_id, data):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        return self._exec("put", "media/%s" % external_id_values["id"], data=data)

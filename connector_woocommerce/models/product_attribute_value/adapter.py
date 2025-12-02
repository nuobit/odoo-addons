# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueAdapter(Component):
    _name = "woocommerce.product.attribute.value.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.attribute.value"

    def read(self, external_id):  # pylint: disable=W8106
        external_id = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/attributes/%s/terms/%s" % tuple(external_id)
        values = self._exec("get", url)
        return values

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id = binder.dict2id(domain_dict, in_field=False)
        if external_id:
            res = self.read(external_id)
            if len(res) > 1:
                raise ValidationError(
                    _("Multiple attribute values found with external_id %s")
                    % (external_id,)
                )
        else:
            if "parent_id" not in domain_dict:
                attribute_adapter = self.component(
                    usage="backend.adapter", model_name="woocommerce.product.attribute"
                )
                attributes = attribute_adapter.search_read([])
                if "parent_name" in domain_dict:
                    attributes = self._filter(
                        attributes, domain=[("name", "=", domain_dict["parent_name"])]
                    )
                attribute_ids = [x["id"] for x in attributes]
                del domain_dict["parent_name"]
            else:
                attribute_ids = [domain_dict["parent_id"]]
                del domain_dict["parent_id"]

            domain = self._normalized_dict_to_domain(domain_dict)
            search_fields = self._get_search_fields()
            real_domain, common_domain = self._extract_domain_clauses(
                domain, search_fields
            )

            attribute_values = []
            for attribute_id in attribute_ids:
                url = "products/attributes/%s/terms" % attribute_id
                values = self._exec("get", url, domain=real_domain)
                for value in values:
                    value["parent_id"] = attribute_id
                attribute_values += values
            res = self._filter(attribute_values, domain=common_domain)

        return res

    def create(self, data):  # pylint: disable=W8106
        if "parent_id" not in data:
            raise ValidationError(
                _("Attribute id is required to create attribute value on woocommerce.")
            )
        res = self._exec(
            "post",
            "products/attributes/%s/terms" % data["parent_id"],
            data=data,
        )
        if res:
            res.update({"parent_id": data["parent_id"]})
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        return self._exec(
            "put",
            "products/attributes/%s/terms/%s" % tuple(external_id),
            data=data,
        )

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.append("slug")
        return res

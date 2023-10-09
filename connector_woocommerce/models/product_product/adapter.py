# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductProductAdapter(Component):
    _name = "woocommerce.product.product.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.product"

    def read(self, external_id):  # pylint: disable=W8106
        external_id = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/%s/variations/%s" % (
            external_id["parent_id"],
            external_id["id"],
        )
        return self._exec("get", url)

    def create(self, data):  # pylint: disable=W8106
        self._prepare_data(data)
        url_l = ["products"]
        parent = data.pop("parent_id")
        url_l.append("%s/variations" % parent)
        res = self._exec("post", "/".join(url_l), data=data)
        res["parent_id"] = parent
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        self._prepare_data(data)
        return self._exec(
            "put",
            "products/%s/variations/%s" % (external_id[0], external_id[1]),
            data=data,
        )

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, external_id_fields)
        external_id = binder.dict2id2dict(domain_dict, in_field=False)
        if external_id:
            url = "products/%s/variations/%s" % (
                external_id["parent_id"],
                external_id["id"],
            )
            res = self._exec("get", url, domain=common_domain)
        else:
            if "id" in domain_dict and "parent_id" in domain_dict:
                url = "products/%s/variations/%s" % (
                    domain_dict["parent_id"],
                    domain_dict["id"],
                )
                res = self._exec("get", url, domain=common_domain)
            elif "sku" in domain_dict:
                url = "products"
                res = self._exec("get", url, domain=domain)
            else:
                raise ValidationError(_("Params required"))
        return res

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.extend(["sku", "parent"])
        return res

    def _format_product_product(self, data):
        conv_mapper = {
            "/regular_price": lambda x: str(round(x, 10)) or None,
        }
        self._convert_format(data, conv_mapper)

    def _prepare_data(self, data):
        self._format_product_product(data)

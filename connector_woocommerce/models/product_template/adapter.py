# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductTemplateAdapter(Component):
    _name = "woocommerce.product.template.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.product.template"

    def create(self, data):  # pylint: disable=W8106
        self._prepare_data(data)
        return self._exec("post", "products", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        self._prepare_data(data)
        url_l = ["products", str(external_id[0])]
        res = self._exec("put", "/".join(url_l), data=data)
        return res

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, id_fields)
        template_id = binder.dict2id(domain_dict, in_field=False, unwrap=True)

        if template_id:
            url = "products/%s" % template_id
            res = self._exec("get", url, domain=common_domain)
        else:
            res = []
            skus = binder.dict2id(
                domain_dict, in_field=False, alt_field=True, unwrap=True
            )
            if skus and len(skus) > 1:
                skus = ",".join([f"{sku}" for sku in skus if sku])
            if skus:
                products = self._exec("get", "products", domain=[("sku", "=", skus)])
                if len(products) == 1 and products[0]["type"] == "simple":
                    return products
                parent_ids = set(filter(None, map(lambda x: x["parent_id"], products)))
                if len(parent_ids) > 1:
                    raise ValidationError(
                        _("All variants must belong to the same parent product")
                    )
                if parent_ids:
                    res = [{"id": parent_ids.pop()}]
            else:
                res = self._exec("get", "products", domain=domain)
        return res

    def _get_filters_values(self):
        res = super()._get_filters_values()
        res.extend(["sku"])
        return res

    def _format_product_template(self, data):
        conv_mapper = {
            "/regular_price": lambda x: str(round(x, 10)) or None,
        }
        self._convert_format(data, conv_mapper)

    def _prepare_data(self, data):
        self._format_product_template(data)
        if data["sku"]:
            if data["type"] == "simple":
                if len(data["sku"]) > 1:
                    raise ValidationError(
                        _("Simple products can only have one variant")
                    )
                else:
                    data["sku"] = data["sku"][0]
            elif data["type"] == "variable":
                data.pop("sku")
            else:
                raise ValidationError(_("Product type not supported"))

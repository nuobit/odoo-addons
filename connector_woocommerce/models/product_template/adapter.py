# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductTemplate(Component):
    _name = "woocommerce.product.template.adapter"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.template"

    def create(self, data):  # pylint: disable=W8106
        if data["type"] == "simple":
            if len(data["sku"]) > 1:
                raise ValidationError(_("Simple products can only have one variant"))
            if data["sku"]:
                data["sku"] = data["sku"][0]
            else:
                data.pop("sku")
        elif data["type"] == "variable":
            data.pop("sku")
        else:
            raise ValidationError(_("Product type not supported"))
        return self._exec("post", "products", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        # TODO: when we do this write, we need to ensure that
        #  the product exists in WooCommerce? (GET?)
        # TODO: REVIEW: if a product is deleted in woocommerce
        #  and we have binding, we need to export it again?
        # if self._exec("get", "products/%s" % external_id, ).get('status')
        # == "Trash":
        #     return self._exec("post", "products/%s" % external_id,
        #     data={'status': 'publish'})
        # elif self._exec("get", "products/%s" % external_id)
        # .get('message') == "Invalid ID":
        #     return self._exec("post", "products", data=data)
        url_l = ["products", str(external_id)]
        return self._exec("put", "/".join(url_l), data=data)

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, external_id_fields)
        # Necessitem el binding per fer aquest dict2id2dict? com l'agafem?
        external_id = binder.dict2id2dict(domain_dict, in_field=False)
        if external_id:
            url = "products/%s" % external_id["id"]
            res = self._exec("get", url, domain=common_domain)
        else:
            if "sku" in domain_dict:
                res = []
                parent = False
                for sku in domain_dict["sku"]:
                    res = self._exec("get", "products", domain=[("sku", "=", sku)])
                    if res:
                        if "parent_id" in res[0]:
                            res_parent = res[0]["parent_id"]
                            if parent:
                                # This bool prevents parent_id = 0 in response
                                if bool(res_parent) and parent != res_parent:
                                    raise ValidationError(
                                        _(
                                            "All variants must belong to "
                                            "the same parent product"
                                        )
                                    )
                            else:
                                if bool(res_parent):
                                    parent = res_parent
                if parent:
                    res = [{"id": parent}]
            else:
                res = self._exec("get", "products", domain=domain)
        return res

    def _get_filters_values(self):
        res = super()._get_filters_values()
        res.extend(["sku"])
        return res

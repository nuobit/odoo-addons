# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductTemplateAdapter(Component):
    _name = "woocommerce.wpml.product.template.adapter"
    _inherit = "connector.woocommerce.wpml.adapter"

    _apply_on = "woocommerce.wpml.product.template"

    def _reorg_product_data(self, data):
        return

    def read(self, external_id):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/%s" % external_id_values["id"]
        res = self._exec("get", url, limit=1)
        self._reorg_product_data(res)
        if len(res) > 1:
            raise ValidationError(
                _("More than one simple product found with the same id: %s")
                % (external_id_values["id"])
            )
        return res[0]

    def create(self, data):  # pylint: disable=W8106
        if data.get("type") == "simple" and data.get("translation_of"):
            data.pop("sku")
        self._prepare_data(data)
        return self._exec("post", "products", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        old_sku = None
        if data.get("type") == "simple":
            old_sku = data.pop("sku")
            if isinstance(old_sku, list):
                old_sku = old_sku[0]
        self._prepare_data(data)
        url_l = ["products", str(external_id[0])]
        res = self._exec("put", "/".join(url_l), data=data)
        if old_sku and res["data"].get("sku") != old_sku:
            data["sku"] = old_sku
            # This conversion is to "revert" first conversion done on prepare_data
            if isinstance(data["regular_price"], str):
                data["regular_price"] = float(data["regular_price"])
            if isinstance(data["regular_price"], str):
                data["sale_price"] = float(data["sale_price"])
            self._prepare_data(data)
            url_l = ["products", str(external_id[0])]
            res = self._exec("put", "/".join(url_l), data=data)
        return res

    def _modify_res_on_search_read(self, parent_ids, domain_dict):
        return [{"id": parent_ids.pop()}]

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        id_fields = binder.get_id_fields(in_field=False)
        __, common_domain = self._extract_domain_clauses(domain, id_fields)
        template_id = binder.dict2id(domain_dict, in_field=False, unwrap=True)
        if template_id:
            url = "products/%s" % template_id
            res = self._exec("get", url, domain=common_domain)
        else:
            res = []
            skus = []
            if "sku" in domain_dict:
                skus = domain_dict["sku"]
            if skus and len(skus) > 1:
                skus = ",".join([f"{sku}" for sku in skus if sku])
            if skus:
                products = self._exec("get", "products", domain=domain)
                if len(products) == 1 and products[0]["type"] == "simple":
                    return products
                parent_ids = set(filter(None, map(lambda x: x["parent_id"], products)))
                if len(parent_ids) > 1:
                    raise ValidationError(
                        _("All variants must belong to the same parent product")
                    )
                if parent_ids:
                    res = self._modify_res_on_search_read(parent_ids, domain_dict)
            else:
                res = self._exec("get", "products", domain=domain)
        return res

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.extend(["sku"])
        return res

    def _format_product_template(self, data):
        conv_mapper = {
            "/regular_price": lambda x: str(round(x, 10)) if x is not None else None,
            "/sale_price": lambda x: str(round(x, 10)) if x is not None else None,
        }
        self._convert_format(data, conv_mapper)

    def _prepare_data(self, data):
        self._format_product_template(data)
        meta_data = self.prepare_meta_data(data)
        if meta_data:
            data["meta_data"] = meta_data
        if data.get("sku"):
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

    # TODO: REVIEW: Try this code
    # TODO: REVIEW: Duplicated name function
    def _get_search_fields(self):
        res = super()._get_search_fields()
        res.append("lang")
        return res

    # TODO: REVIEW: Duplicated name function
    def _modify_res_on_search_read(self, parent_ids, domain_dict):
        res = super()._modify_res_on_search_read(parent_ids, domain_dict)
        res[0]["lang"] = domain_dict.get("lang")
        return res

    def _domain_to_normalized_dict(self, real_domain):
        domain = super()._domain_to_normalized_dict(real_domain)
        if not domain.get("lang"):
            domain["lang"] = "all"
        return domain

    def _extract_domain_clauses(self, domain, search_fields):
        real_domain, common_domain = super()._extract_domain_clauses(
            domain, search_fields
        )
        lang_clause_exists = any(clause[0] == "lang" for clause in common_domain)
        for clause in domain:
            if "lang" in clause[0] and not lang_clause_exists:
                common_domain.append(clause)
        return real_domain, common_domain

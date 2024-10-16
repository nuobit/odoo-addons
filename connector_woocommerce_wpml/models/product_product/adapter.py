# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductProductAdapter(Component):
    _name = "woocommerce.wpml.product.product.adapter"
    _inherit = "connector.woocommerce.wpml.adapter"

    _apply_on = "woocommerce.wpml.product.product"

    # class WooCommerceProductProductAdapter(Component):
    #     _name = "woocommerce.product.product.adapter"
    #     _inherit = [
    #         "woocommerce.product.product.adapter",
    #         "woocommerce.product.wpml.mixin.adapter",
    #     ]
    def _reorg_product_data(self, data):
        return

    def read(self, external_id):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/%s/variations/%s" % (
            external_id_values["parent_id"],
            external_id_values["id"],
        )
        res = self._exec("get", url, limit=1)
        self._reorg_product_data(res)
        if len(res) > 1:
            raise ValidationError(
                _("More than one simple product found with the same id: %s")
                % (external_id_values["id"])
            )
        return res[0]

    def create(self, data):  # pylint: disable=W8106
        if data.get("translation_of"):
            data.pop("sku")
        self._prepare_data(data)
        url_l = ["products"]
        parent = data.pop("parent_id")
        url_l.append("%s/variations" % parent)
        res = self._exec("post", "/".join(url_l), data=data)
        res["parent_id"] = parent
        return res

    def write(self, external_id, data):  # pylint: disable=W8106
        old_sku = None
        if data.get("sku"):
            old_sku = data.pop("sku")
        self._prepare_data(data)
        res = self._exec(
            "put",
            "products/%s/variations/%s" % (external_id[0], external_id[1]),
            data=data,
        )
        if old_sku and res.get("data").get("sku") != old_sku:
            data["sku"] = old_sku
            self._prepare_data(data)
            res = self._exec(
                "put",
                "products/%s/variations/%s" % (external_id[0], external_id[1]),
                data=data,
            )
        return res

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, external_id_fields)
        external_id_values = binder.dict2id2dict(domain_dict, in_field=False)
        if external_id_values:
            url = "products/%s/variations/%s" % (
                external_id_values["parent_id"],
                external_id_values["id"],
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
        res.extend(["sku", "parent", "lang"])
        return res

    def _format_product_product(self, data):
        conv_mapper = {
            "/regular_price": lambda x: str(round(x, 10)) if x is not None else None,
            "/sale_price": lambda x: str(round(x, 10)) if x is not None else None,
        }
        self._convert_format(data, conv_mapper)

    def _prepare_data(self, data):
        self._format_product_product(data)

    def _domain_to_normalized_dict(self, real_domain):
        domain = super()._domain_to_normalized_dict(real_domain)
        if not domain.get("lang"):
            domain["lang"] = "all"
        return domain

    # on Product variations the query return all variations with sku
    def _extract_domain_clauses(self, domain, search_fields):
        real_domain, common_domain = super()._extract_domain_clauses(
            domain, search_fields
        )
        for clause in domain:
            if "lang" in clause[0]:
                common_domain.append(clause)
        return real_domain, common_domain

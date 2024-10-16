# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceWPMLProductPublicCategoryAdapter(Component):
    _name = "woocommerce.wpml.product.public.category.adapter"
    _inherit = "connector.woocommerce.wpml.adapter"

    _apply_on = "woocommerce.wpml.product.public.category"
    # _inherit = "woocommerce.product.public.category.adapter"
    # _name = "woocommerce.product.public.category.adapter"
    # _inherit = [
    #     "woocommerce.product.public.category.adapter",
    #     "woocommerce.product.wpml.mixin.adapter",
    # ]

    def create(self, data):  # pylint: disable=W8106
        return self._exec("post", "products/categories", data=data)

    def write(self, external_id, data):  # pylint: disable=W8106
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/categories/%s" % external_id_values["id"]
        return self._exec("put", url, data=data)

    def search_read(self, domain=None):
        return self._exec("get", "products/categories", domain=domain)

    def _get_search_fields(self):
        res = super()._get_search_fields()
        res += ["slug", "lang"]
        return res

    def delete(self, external_id):
        external_id_values = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/categories/%s" % external_id_values["id"]
        return self._exec("delete", url, params={"force": "1"})

    def _manage_error_codes(
        self, res_data, res, resource, raise_on_error=True, **kwargs
    ):
        if res.status_code == 500:
            if res_data.get("code") == "duplicate_term_slug":
                error_message = _(
                    "Error: '%s'. "
                    "WPML plugin allows set the same slug for different "
                    "languages on FrontEnd but this can't be done via API. "
                    "Probably we need a solution in plugin code, it can't "
                    "be solved in Odoo without a workaround modifying raw data. "
                    "Review the slug of the category '%s' in lang [%s] and try again."
                    ""
                    % (
                        res_data["message"],
                        kwargs["data"].get("name"),
                        kwargs["data"].get("lang"),
                    )
                )
                if raise_on_error:
                    raise ValidationError(error_message)
                else:
                    return error_message

        return super()._manage_error_codes(
            res_data, res, resource, raise_on_error=True, **kwargs
        )

    #
    # def _get_search_fields(self):
    #     return self.wpml_get_search_fields()

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

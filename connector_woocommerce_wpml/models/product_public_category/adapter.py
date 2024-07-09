# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryAdapter(Component):
    _name = "woocommerce.product.public.category.adapter"
    _inherit = [
        "woocommerce.product.public.category.adapter",
        "woocommerce.product.wpml.mixin.adapter",
    ]

    def _manage_error_codes(
        self, res_data, res, resource, raise_on_error=True, **kwargs
    ):
        if res.status_code == 400:
            if res_data.get("code") == "term_exists":
                res = self.search_read(
                    domain=[("id", "=", res_data["res_data"]["resource_id"])]
                )
                if res and len(res) == 1:
                    kwargs["data"]["slug"] = (
                        res[0].get("slug") + "-" + kwargs["data"]["lang"]
                    )
                    res = self._exec_wcapi_call("post", resource, data=kwargs["data"])
                    return res["data"]
        return super()._manage_error_codes(
            res_data, res, resource, raise_on_error=True, **kwargs
        )

    def _get_search_fields(self):
        return self.wpml_get_search_fields()

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    # def _extract_domain_clauses(self, domain, search_fields):
    #     return self.wpml_extract_domain_clauses(domain, search_fields)

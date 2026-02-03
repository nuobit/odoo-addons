# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryAdapter(Component):
    _name = "woocommerce.product.public.category.adapter"
    _inherit = [
        "woocommerce.product.public.category.adapter",
        "woocommerce.product.wpml.mixin.adapter",
    ]

    def _manage_error_codes(
        self, op, res_data, res, resource, *args, raise_on_error=True, **kwargs
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
            op, res_data, res, resource, *args, raise_on_error=raise_on_error, **kwargs
        )

    def _get_search_fields(self):
        return self.wpml_get_search_fields()

    # def _get_search_fields(self):
    #     res_new = []
    #     res = self.wpml_get_search_fields()
    #     # Workaround for a WooCommerce API bug: the API sometimes fails to filter by
    #     # language. This is another bug in the WPML API. Because of this, we cannot
    #     # rely on server-side filtering. There is no other option but to fetch all
    #     # records and filter them locally (inefficient, but reliable). If the WPML
    #     # WooCommerce API is fixed in the future, we can keep the language as a
    #     # search field and perform server-side filtering instead of removing it here.
    #     # With the version 1.0.3 of the WooCommerce plugin this should not be necessary
    #     # https://github.com/nuobit/woocommerce-wpml-api-rest-extension
    #     for f in res:
    #         if f != "lang":
    #             res_new.append(f)
    #     return res_new

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    def _extract_domain_clauses(self, domain, search_fields):
        return self.wpml_extract_domain_clauses(domain, search_fields)

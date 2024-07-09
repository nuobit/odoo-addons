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

    def _get_search_fields(self):
        return self.wpml_get_search_fields()

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    def _extract_domain_clauses(self, domain, search_fields):
        return self.wpml_extract_domain_clauses(domain, search_fields)

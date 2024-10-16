# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductPublicCategoryBinder(Component):
    _name = "woocommerce.wpml.product.public.category.binder"
    _inherit = "woocommerce.wpml.binder"

    _apply_on = "woocommerce.wpml.product.public.category"

    external_id = ["id"]
    internal_id = ["woocommerce_wpml_idpubliccategory"]
    external_alt_id = ["name", "lang"]

    def get_binding_domain(self, record):
        domain = super().get_binding_domain(record)
        wp_wpml_code = self.env["res.lang"]._get_wpml_code_from_iso_code(
            record._context.get("lang")
        )
        if wp_wpml_code:
            domain += [
                (
                    "woocommerce_lang",
                    "=",
                    wp_wpml_code,
                )
            ]
        return domain

    def _additional_external_binding_fields(self, external_data):
        return {
            **super()._additional_external_binding_fields(external_data),
            "woocommerce_lang": external_data["lang"],
        }

    # def unwrap_binding(self, binding):
    #     res = super().unwrap_binding(binding)
    #     if isinstance(binding.mapped(self._odoo_field), models.BaseModel):
    #         res = res.with_context(lang=binding.woocommerce_lang)
    #     return res

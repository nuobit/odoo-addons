# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductAttributeValueBinder(Component):
    _name = "woocommerce.wpml.product.attribute.value.binder"
    _inherit = "woocommerce.wpml.binder"

    _apply_on = "woocommerce.wpml.product.attribute.value"
    # _name = "woocommerce.product.attribute.value.binder"
    # _inherit = [
    #     "woocommerce.product.attribute.value.binder",
    #     "woocommerce.product.wpml.mixin.binder",
    # ]

    external_id = ["parent_id", "id"]
    internal_id = ["woocommerce_wpml_idattribute", "woocommerce_wpml_idattributevalue"]
    external_alt_id = ["parent_name", "name", "lang"]

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
    #     return self.wpml_unwrap_binding(binding)

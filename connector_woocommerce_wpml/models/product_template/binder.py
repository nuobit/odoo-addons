# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductTemplateBinder(Component):
    _name = "woocommerce.wpml.product.template.binder"
    _inherit = "woocommerce.wpml.binder"

    _apply_on = "woocommerce.wpml.product.template"

    external_id = ["id"]
    internal_id = ["woocommerce_wpml_idproduct"]
    external_alt_id = ["sku", "lang"]
    internal_alt_id = ["default_code"]

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

    # We need this because we can't filter sku and lang
    def _get_external_record_alt(self, relation, id_values):
        res = super()._get_external_record_alt(relation, id_values)
        if res:
            relation_wp_lang = self.env["res.lang"]._get_wpml_code_from_iso_code(
                relation.env.context.get("lang")
            )
            if res.get("lang") != relation_wp_lang:
                if res.get("translations") and res["translations"].get(
                    relation_wp_lang
                ):
                    adapter = self.component(usage="backend.adapter")
                    res = adapter.read(res["translations"][relation_wp_lang])
                else:
                    return None
        return res

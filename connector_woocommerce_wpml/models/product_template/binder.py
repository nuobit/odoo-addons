# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBinder(Component):
    _name = "woocommerce.product.template.binder"
    _inherit = [
        "woocommerce.product.template.binder",
        "woocommerce.product.wpml.mixin.binder",
    ]

    @property
    def external_alt_id(self):
        return super().external_alt_id + ["lang"]

    def get_binding_domain(self, record):
        return self.wpml_get_binding_domain(record)

    def _additional_external_binding_fields(self, external_data):
        return self.wpml_additional_external_binding_fields(external_data)

    def unwrap_binding(self, binding):
        return self.wpml_unwrap_binding(binding)

    # We need this because we can't filter sku and lang
    def _get_external_record_alt(self, relation, id_values):
        res = super()._get_external_record_alt(relation, id_values)
        if res:
            relation_lang = relation.env.context.get("lang")
            relation_woo_lang = self.backend_record._get_woocommerce_lang(relation_lang)
            if res.get("lang") != relation_woo_lang:
                if res.get("translations") and res["translations"].get(
                    relation_woo_lang
                ):
                    adapter = self.component(usage="backend.adapter")
                    res = adapter.read(res["translations"][relation_woo_lang])
                else:
                    return None
        return res

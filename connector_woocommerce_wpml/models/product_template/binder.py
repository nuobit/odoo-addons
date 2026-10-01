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

    def _additional_external_binding_fields(self, external_data, relation):
        return self.wpml_additional_external_binding_fields(external_data, relation)

    def wpml_additional_external_binding_fields(self, external_data, relation):
        return {
            **super().wpml_additional_external_binding_fields(external_data, relation),
            "woocommerce_master_lang": relation._context["first_lang"],
        }

    # def unwrap_binding(self, binding):
    #     return self.wpml_unwrap_binding(binding)

    # We need this because we can't filter sku and lang
    def _get_external_record_alt(self, relation, id_values):
        res = super()._get_external_record_alt(relation, id_values)
        if res:
            res = self._wpml_redirect_record_lang(relation, res)
        return res

    def _get_external_record_alt_fallback(self, relation, id_values):
        record = super()._get_external_record_alt_fallback(relation, id_values)
        if record:
            record = self._wpml_redirect_record_lang(relation, record)
        return record or {}

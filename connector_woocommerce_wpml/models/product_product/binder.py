# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBinder(Component):
    _name = "woocommerce.product.product.binder"
    _inherit = [
        "woocommerce.product.product.binder",
        "woocommerce.product.wpml.mixin.binder",
    ]
    # _inherit = "woocommerce.product.product.binder"

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

    # TODO: code commented. It's not necessary? delete!
    # def to_external(self, binding, wrap=True, binding_extra_vals=None):
    #     return super().to_external(
    #         binding, wrap=wrap, binding_extra_vals={"lang": binding.woocommerce_lang}
    #     )

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

    def _wpml_read_translation(self, relation, record, translation_id):
        # A variation is read under its parent product: resolve the parent
        # for the requested language through the template binding.
        template_binder = self.binder_for("woocommerce.product.template")
        template_binding = template_binder.wrap_record(relation.product_tmpl_id)
        if not template_binding:
            return None
        adapter = self.component(usage="backend.adapter")
        return adapter.read([template_binding.woocommerce_idproduct, translation_id])

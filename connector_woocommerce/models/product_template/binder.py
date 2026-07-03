# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBinder(Component):
    _name = "woocommerce.product.template.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.product.template"

    @property
    def external_id(self):
        return ["id"]

    @property
    def internal_id(self):
        return ["woocommerce_idproduct"]

    @property
    def external_alt_id(self):
        return ["sku"]

    @property
    def internal_alt_id(self):
        return ["default_code"]

    def _get_external_record_alt_fallback(self, relation, id_values):
        # A variable product template carries no SKU of its own on WooCommerce
        # (the SKUs belong to its variations), so it can never be found through
        # the alternate key. Derive the external parent product through one of
        # its variations instead.
        if not relation.has_attributes:
            return super()._get_external_record_alt_fallback(relation, id_values)
        adapter = self.component(usage="backend.adapter")
        variants = relation.with_context(active_test=False).product_variant_ids
        for binding in variants.woocommerce_bind_ids.filtered(
            lambda x: x.backend_id == self.backend_record
        ):
            if binding.woocommerce_idparent:
                return adapter.read(binding.woocommerce_idparent)
        variation_adapter = self.component(
            usage="backend.adapter", model_name="woocommerce.product.product"
        )
        for sku in variants.filtered("default_code").mapped("default_code"):
            for variation in variation_adapter.search_read([("sku", "=", sku)]):
                if variation.get("parent_id"):
                    return adapter.read(variation["parent_id"])
        return super()._get_external_record_alt_fallback(relation, id_values)

    # def _additional_external_binding_fields(self, external_data, relation):
    #     return {
    #         **super()._additional_external_binding_fields(external_data, relation),
    #     }

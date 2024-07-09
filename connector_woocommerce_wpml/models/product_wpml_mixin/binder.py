# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductWPMLMixinBinder(AbstractComponent):
    _name = "woocommerce.product.wpml.mixin.binder"
    _inherit = "connector.extension.generic.binder"

    def wpml_get_binding_domain(self, record):
        domain = super().get_binding_domain(record)
        lang_code = record._context.get("lang")
        if lang_code:
            domain += [
                (
                    "woocommerce_lang",
                    "=",
                    self.backend_record._get_woocommerce_lang(lang_code),
                )
            ]
        return domain

    def wpml_additional_external_binding_fields(self, external_data, relation):
        return {
            **super()._additional_external_binding_fields(external_data, relation),
            "woocommerce_lang": external_data["lang"],
        }

    def wpml_unwrap_binding(self, binding):
        res = super().unwrap_binding(binding)
        if res:
            context = res.env.context.copy()
            mapped_lang = self.backend_record.wpml_lang_map_ids.filtered(
                lambda x: binding.woocommerce_lang == x.woocommerce_wpml_lang
            )
            if mapped_lang:
                context.update(
                    {"lang": mapped_lang.lang_id.code, "resync_export": True}
                )
                res.env.context = context
        return res

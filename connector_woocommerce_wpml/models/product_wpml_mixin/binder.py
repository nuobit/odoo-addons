# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductWPMLMixinBinder(AbstractComponent):
    _name = "woocommerce.product.wpml.mixin.binder"
    _inherit = "connector.extension.generic.binder"

    def wpml_get_binding_domain(self, record):
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

    def wpml_additional_external_binding_fields(self, external_data):
        # TODO: this additional fields probably should be
        #  included in binding as m2o to res lang on upper binder
        return {
            **super()._additional_external_binding_fields(external_data),
            "woocommerce_lang": external_data["lang"],
        }

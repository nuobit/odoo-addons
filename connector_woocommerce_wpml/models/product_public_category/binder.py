# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductPublicCategoryBinder(AbstractComponent):
    _name = "woocommerce.product.public.category.binder"
    _inherit = [
        "woocommerce.product.public.category.binder",
        "woocommerce.product.wpml.mixin.binder",
    ]

    @property
    def external_alt_id(self):
        return super().external_alt_id + ["lang"]

    def get_binding_domain(self, record):
        return self.wpml_get_binding_domain(record)

    def _additional_external_binding_fields(self, external_data, relation):
        return self.wpml_additional_external_binding_fields(external_data, relation)

    def unwrap_binding(self, binding):
        return self.wpml_unwrap_binding(binding)

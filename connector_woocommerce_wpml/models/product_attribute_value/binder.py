# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueBinder(Component):
    _name = "woocommerce.product.attribute.value.binder"
    _inherit = [
        "woocommerce.product.attribute.value.binder",
        "woocommerce.product.wpml.mixin.binder",
    ]

    @property
    def external_alt_id(self):
        return super().external_alt_id + ["lang"]

    def get_binding_domain(self, record):
        return self.wpml_get_binding_domain(record)

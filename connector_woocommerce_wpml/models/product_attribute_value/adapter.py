# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeValueAdapter(Component):
    _name = "woocommerce.product.attribute.value.adapter"
    _inherit = [
        "woocommerce.product.attribute.value.adapter",
        "woocommerce.product.wpml.mixin.adapter",
    ]

    def _get_search_fields(self):
        return self.wpml_get_search_fields()

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    # def _extract_domain_clauses(self, domain, search_fields):
    #     return self.wpml_extract_domain_clauses(domain, search_fields)

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductWPMLMixinAdapter(AbstractComponent):
    _name = "woocommerce.product.wpml.mixin.adapter"
    _inherit = "connector.extension.woocommerce.adapter.crud"

    def wpml_get_search_fields(self):
        res = super()._get_search_fields()
        res.append("lang")
        return res

    def wpml_domain_to_normalized_dict(self, real_domain):
        domain = super()._domain_to_normalized_dict(real_domain)
        if domain.get("lang"):
            domain["lang"] = "all"
        return domain

    def wpml_extract_domain_clauses(self, domain, search_fields):
        real_domain, common_domain = super()._extract_domain_clauses(
            domain, search_fields
        )
        for clause in domain:
            if "lang" in clause[0]:
                common_domain.append(clause)
        return real_domain, common_domain

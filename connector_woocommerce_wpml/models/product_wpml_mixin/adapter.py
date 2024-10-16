# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


# TODO: we shoudn't need to use this if we do component aproach.
class WooCommerceWPMLProductWPMLMixinAdapter(AbstractComponent):
    _name = "woocommerce.wpml.product.wpml.mixin.adapter"
    _inherit = "connector.extension.woocommerce.adapter.crud"

    def wpml_get_search_fields(self):
        res = super()._get_search_fields()
        res.append("lang")
        return res

    def wpml_domain_to_normalized_dict(self, real_domain):
        domain = super()._domain_to_normalized_dict(real_domain)
        if not domain.get("lang"):
            domain["lang"] = "all"
        return domain

    def wpml_extract_domain_clauses(self, domain, search_fields):
        real_domain, common_domain = super()._extract_domain_clauses(
            domain, search_fields
        )
        lang_clause_exists = any(clause[0] == "lang" for clause in common_domain)
        for clause in domain:
            if "lang" in clause[0] and not lang_clause_exists:
                common_domain.append(clause)
        return real_domain, common_domain

# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductAdapter(Component):
    _name = "woocommerce.product.product.adapter"
    _inherit = [
        "woocommerce.product.product.adapter",
        "woocommerce.product.wpml.mixin.adapter",
    ]

    # TODO AQUI: do we need this 2 next methods
    # def create(self, data):
    #     if data.get("translation_of"):
    #         sku = data.pop("sku")
    #     res = super().create(data)
    #     if data.get("translation_of"):
    #         if res and isinstance(res, dict):
    #             external_id = res.get("id")
    #             parent_id = res.get("parent_id")
    #             if external_id:
    #                 url_l = "products/%s/variations/%s" % (parent_id, external_id)
    #                 self._exec("put", url_l, data={"sku": sku})
    #     return res

    # def write(self, external_id, data):  # pylint: disable=W8106
    #     old_sku = None
    #     if data.get("sku"):
    #         old_sku = data.pop("sku")
    #     res = super().write(external_id, data)
    #     if old_sku and res.get("data").get("sku") != old_sku:
    #         data["sku"] = old_sku
    #         res = super().write(external_id, data)
    #     return res

    # TODO: REVIEW: can we return this in better way?
    def _get_search_fields(self):
        res = list(
            set(self.wpml_get_search_fields()) | set(super()._get_search_fields())
        )
        return res

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    # on Product variations the query return all variations with sku
    def _extract_domain_clauses(self, domain, search_fields):
        real_domain, common_domain = super()._extract_domain_clauses(
            domain, search_fields
        )
        for clause in domain:
            if "lang" in clause[0]:
                common_domain.append(clause)
        return real_domain, common_domain

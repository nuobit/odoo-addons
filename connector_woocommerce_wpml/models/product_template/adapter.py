# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateAdapter(Component):
    _name = "woocommerce.product.template.adapter"
    _inherit = [
        "woocommerce.product.template.adapter",
        "woocommerce.product.wpml.mixin.adapter",
    ]

    def create(self, data):
        if data.get("type") == "simple" and data.get("translation_of"):
            data.pop("sku")
        return super().create(data)

    def write(self, external_id, data):  # pylint: disable=W8106
        old_sku = None
        if data.get("type") == "simple":
            old_sku = data.pop("sku")
        res = super().write(external_id, data)
        if old_sku and res.get("sku") != old_sku:
            data["sku"] = old_sku
            res = super().write(external_id, data)
        return res

    # TODO: REVIEW: can we return this in better way?
    def _get_search_fields(self):
        return list(
            set(self.wpml_get_search_fields()) | set(super()._get_search_fields())
        )

    # We need to override this method to handle the case when the response is a single item,
    # because parameter X-WP-Total is not included in header
    # def _get_res_total_items(self, res):
    #     total_items = super()._get_res_total_items(res)
    #     if not total_items:
    #         res_data = res.json()
    #         if isinstance(res_data, dict) and res_data:
    #             total_items = 1
    #     return total_items

    # def _domain_to_normalized_dict(self, real_domain):
    #     return self.wpml_domain_to_normalized_dict(real_domain)

    # def _extract_domain_clauses(self, domain, search_fields):
    #     return self.wpml_extract_domain_clauses(domain, search_fields)

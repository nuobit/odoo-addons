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
            # This conversion is to "revert" first conversion done on prepare_data
            if isinstance(data["regular_price"], str):
                data["regular_price"] = float(data["regular_price"])
            res = super().write(external_id, data)
        return res

    # TODO: REVIEW: can we return this in better way?
    def _get_search_fields(self):
        return list(
            set(self.wpml_get_search_fields()) | set(super()._get_search_fields())
        )

    def _modify_res_on_search_read(self, parent_ids, domain_dict):
        res = super()._modify_res_on_search_read(parent_ids, domain_dict)
        res[0]["lang"] = domain_dict.get("lang")

    def _domain_to_normalized_dict(self, real_domain):
        return self.wpml_domain_to_normalized_dict(real_domain)

    def _extract_domain_clauses(self, domain, search_fields):
        return self.wpml_extract_domain_clauses(domain, search_fields)

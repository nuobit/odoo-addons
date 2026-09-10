# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.osv import expression


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _woocommerce_get_affected_products(self):
        templates = self.env["product.template"].with_context(active_test=False)
        variants = self.env["product.product"].with_context(active_test=False)
        discount_pricelists = (
            self.env["woocommerce.backend"]
            .with_context(active_test=False)
            .search([("discount_pricelist_id", "in", self.pricelist_id.ids)])
            .discount_pricelist_id
        )
        rules = self.filtered(lambda item: item.pricelist_id in discount_pricelists)
        if not rules:
            return templates, variants

        template_domains = []
        variant_domains = []
        for rule in rules:
            if rule.applied_on == "0_product_variant":
                template_domains.append(
                    [("id", "in", rule.product_id.product_tmpl_id.ids)]
                )
                variant_domains.append([("id", "in", rule.product_id.ids)])
            elif rule.applied_on == "1_product":
                template_domains.append([("id", "in", rule.product_tmpl_id.ids)])
                variant_domains.append(
                    [("product_tmpl_id", "in", rule.product_tmpl_id.ids)]
                )
            elif rule.applied_on == "2_product_category":
                category_domain = [("categ_id", "child_of", rule.categ_id.ids)]
                template_domains.append(category_domain)
                variant_domains.append(category_domain)
            else:
                template_domains = [expression.TRUE_DOMAIN]
                variant_domains = [expression.TRUE_DOMAIN]
                break

        bound_domain = [("woocommerce_bind_ids", "!=", False)]
        return (
            templates.search(
                expression.AND([bound_domain, expression.OR(template_domains)])
            ),
            variants.search(
                expression.AND([bound_domain, expression.OR(variant_domains)])
            ),
        )

    def _woocommerce_touch(self, *recordsets):
        now = fields.Datetime.now()
        for records in recordsets:
            records.woocommerce_write_date = now

    def _dependent_field_product_woocommerce_write_date(self):
        return {
            "product_id",
            "product_tmpl_id",
            "categ_id",
            "applied_on",
            "pricelist_id",
            "compute_price",
            "fixed_price",
            "percent_price",
            "price_discount",
            "price_surcharge",
            "price_round",
            "price_min_margin",
            "price_max_margin",
            "base",
            "base_pricelist_id",
            "min_quantity",
            "date_start",
            "date_end",
            "active",
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._woocommerce_touch(*records._woocommerce_get_affected_products())
        return records

    def write(self, values):
        if not self._dependent_field_product_woocommerce_write_date() & values.keys():
            return super().write(values)
        templates, variants = self._woocommerce_get_affected_products()
        result = super().write(values)
        new_templates, new_variants = self._woocommerce_get_affected_products()
        self._woocommerce_touch(templates | new_templates, variants | new_variants)
        return result

    def unlink(self):
        self._woocommerce_touch(*self._woocommerce_get_affected_products())
        return super().unlink()

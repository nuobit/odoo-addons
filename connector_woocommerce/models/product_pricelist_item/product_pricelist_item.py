# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.osv import expression


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _woocommerce_get_discount_pricelist_rules(self):
        """The rules among these that a WooCommerce backend consults through its
        discount pricelist, directly or as one of its base pricelists.
        """
        discount_pricelists = (
            self.env["woocommerce.backend"]
            .with_context(active_test=False)
            .search([("discount_pricelist_id", "!=", False)])
            .discount_pricelist_id._get_woocommerce_pricelist_dependencies()
        )
        return self.filtered(lambda item: item.pricelist_id in discount_pricelists)

    def _woocommerce_get_affected_variants(self):
        """Variants these rules can change, bound to WooCommerce directly or
        through their template: a simple product is its one variant.
        """
        variants = self.env["product.product"].with_context(active_test=False)
        if not self:
            return variants

        domains = []
        for rule in self:
            if rule.applied_on == "0_product_variant":
                domains.append([("id", "in", rule.product_id.ids)])
            elif rule.applied_on == "1_product":
                domains.append([("product_tmpl_id", "in", rule.product_tmpl_id.ids)])
            elif rule.applied_on == "2_product_category":
                domains.append([("categ_id", "child_of", rule.categ_id.ids)])
            else:
                domains = [expression.TRUE_DOMAIN]
                break

        bound_domain = [
            "|",
            ("woocommerce_bind_ids", "!=", False),
            ("product_tmpl_id.woocommerce_bind_ids", "!=", False),
        ]
        return variants.search(expression.AND([bound_domain, expression.OR(domains)]))

    def _woocommerce_touch(self, variants):
        """Mark the variants and their templates for export. Which side WooCommerce
        receives, a simple template or the variants of a variable one, is decided
        by the export batch domains, not here.
        """
        now = fields.Datetime.now()
        variants.woocommerce_write_date = now
        variants.product_tmpl_id.woocommerce_write_date = now

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
        rules = records._woocommerce_get_discount_pricelist_rules()
        records._woocommerce_touch(rules._woocommerce_get_affected_variants())
        return records

    def write(self, values):
        if not self._dependent_field_product_woocommerce_write_date() & values.keys():
            return super().write(values)
        rules = self._woocommerce_get_discount_pricelist_rules()
        variants = rules._woocommerce_get_affected_variants()
        result = super().write(values)
        rules = self._woocommerce_get_discount_pricelist_rules()
        self._woocommerce_touch(variants | rules._woocommerce_get_affected_variants())
        return result

    def unlink(self):
        rules = self._woocommerce_get_discount_pricelist_rules()
        self._woocommerce_touch(rules._woocommerce_get_affected_variants())
        return super().unlink()

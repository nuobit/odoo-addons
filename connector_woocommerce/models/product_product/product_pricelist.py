# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_woocommerce_sale_rule(self, variant, regular_price):
        """Select the current or next discounted price and rule for one unit.

        Return (None, an empty rule recordset) when no offer qualifies.
        """
        self.ensure_one()
        variant.ensure_one()
        now = fields.Datetime.now()
        price, rule_id = self.get_product_price_rule(variant, 1, False, date=now)
        rule_model = self.env["product.pricelist.item"]
        if rule_id and price < regular_price:
            return price, rule_model.browse(rule_id)

        future_rules = rule_model.search(
            [
                ("pricelist_id", "=", self.id),
                ("active", "=", True),
                ("date_start", ">", now),
                ("min_quantity", "<=", 1),
                "|",
                ("product_tmpl_id", "=", False),
                ("product_tmpl_id", "=", variant.product_tmpl_id.id),
                "|",
                ("product_id", "=", False),
                ("product_id", "=", variant.id),
                "|",
                ("categ_id", "=", False),
                ("categ_id", "parent_of", variant.categ_id.id),
            ],
            order="date_start, id",
        )
        for candidate in future_rules:
            # Let the pricelist resolve precedence, percentages and formulas.
            price, rule_id = self.get_product_price_rule(
                variant, 1, False, date=candidate.date_start
            )
            if rule_id and price < regular_price:
                return price, rule_model.browse(rule_id)
        return None, rule_model

    def write(self, values):
        if "active" not in values:
            return super().write(values)
        # Item.active is related: archiving the list does not call item.write().
        rules = (
            self.env["product.pricelist.item"]
            .with_context(active_test=False)
            .search([("pricelist_id", "in", self.ids)])
        )
        templates, variants = rules._woocommerce_get_affected_products()
        result = super().write(values)
        rules._woocommerce_touch(templates, variants)
        return result

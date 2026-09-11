# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_woocommerce_sale_rule(self, variant):
        """Select the currently applicable price and rule for one unit.

        The price is sent as is: whether it is an offer is WooCommerce's call.
        Return (None, an empty rule recordset) when no rule applies.
        """
        self.ensure_one()
        variant.ensure_one()
        now = fields.Datetime.now()
        price, rule_id = self.get_product_price_rule(variant, 1, False, date=now)
        rule_model = self.env["product.pricelist.item"]
        if rule_id:
            return price, rule_model.browse(rule_id)

        return None, rule_model

    def _get_woocommerce_pricelist_dependencies(self):
        """Return these lists and every base list they can consult."""
        pricelists = self.with_context(active_test=False)
        pending = pricelists
        while pending:
            dependencies = pending.item_ids.filtered(
                lambda item: item.base == "pricelist"
            ).base_pricelist_id
            pending = dependencies - pricelists
            pricelists |= pending
        return pricelists

    def _get_woocommerce_transition_rules(self, since_date, until_date):
        """Find validity boundaries crossed since the previous export launch."""
        rules = self.env["product.pricelist.item"]
        if not self or not since_date:
            return rules
        # Odoo includes both endpoints: start applies at equality, end expires after it.
        return rules.search(
            [
                (
                    "pricelist_id",
                    "in",
                    self._get_woocommerce_pricelist_dependencies().ids,
                ),
                ("min_quantity", "<=", 1),
                "|",
                "&",
                ("date_start", ">", since_date),
                ("date_start", "<=", until_date),
                "&",
                ("date_end", ">=", since_date),
                ("date_end", "<", until_date),
            ]
        )

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

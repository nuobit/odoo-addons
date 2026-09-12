# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_woocommerce_sale_price(self, variant):
        """Price this list gives one unit of the variant right now, or None when
        no rule applies. The price is sent as is: whether it is an offer is
        WooCommerce's call.
        """
        if not self or not variant:
            return None
        self.ensure_one()
        variant.ensure_one()
        now = fields.Datetime.now()
        price, rule_id = self.get_product_price_rule(variant, 1, False, date=now)
        return price if rule_id else None

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
        """Rules whose validity starts or ends between the two dates."""
        if not since_date:
            raise ValueError("A transition window needs a start date.")
        rules = self.env["product.pricelist.item"]
        if not self:
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

    def _get_woocommerce_transition_variants(self, since_date, until_date):
        """Variants whose discount rule starts or ends between the two dates. A
        rule crossing one of its dates fires no event: the launcher that owns the
        window asks for them and marks the side it exports.
        """
        rules = self._get_woocommerce_transition_rules(since_date, until_date)
        return rules._woocommerce_get_affected_variants()

    def write(self, values):
        if "active" not in values:
            return super().write(values)
        # Item.active is related: archiving the list does not call item.write().
        rules = (
            self.env["product.pricelist.item"]
            .with_context(active_test=False)
            .search([("pricelist_id", "in", self.ids)])
        )
        discount_rules = rules._woocommerce_get_discount_pricelist_rules()
        variants = discount_rules._woocommerce_get_affected_variants()
        result = super().write(values)
        variants._woocommerce_touch()
        return result

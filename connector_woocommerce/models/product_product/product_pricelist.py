# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

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

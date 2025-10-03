# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    exclude_internal_operations = fields.Boolean(
        string="Exclude internal operations", default=False
    )

    def _excluded_picking_types(self):
        return ["internal"]

    def _get_putaway_location(
        self, product, quantity=0, package=None, packaging=None, qty_by_location=None
    ):
        picking_type_code = self.env.context.get("stock_picking_type_code", False)
        excluded_picking_types = self._excluded_picking_types()
        if (
            picking_type_code in excluded_picking_types
            and self.exclude_internal_operations
        ):
            return self.env["stock.location"]
        return super()._get_putaway_location(
            product, quantity, package, packaging, qty_by_location
        )

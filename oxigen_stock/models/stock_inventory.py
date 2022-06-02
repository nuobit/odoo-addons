# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.tools import float_compare


class OxigenInventory(models.Model):
    _inherit = "stock.inventory"

    location_ids = fields.Many2many(domain="[('company_id', '=', company_id)]")

    def action_validate(self):
        if not self.exists():
            return
        if self.user_has_groups("stock.group_stock_manager") or self.state != "confirm":
            return super().action_validate()
        self.ensure_one()
        inventory_lines = self.line_ids.filtered(
            lambda l: l.product_id.tracking in ["lot", "serial"]
            and not l.prod_lot_id
            and l.theoretical_qty != l.product_qty
        )
        lines = self.line_ids.filtered(
            lambda l: float_compare(
                l.product_qty, 1, precision_rounding=l.product_uom_id.rounding
            )
            > 0
            and l.product_id.tracking == "serial"
            and l.prod_lot_id
        )
        if inventory_lines and not lines:
            wiz_lines = [
                (0, 0, {"product_id": product.id, "tracking": product.tracking})
                for product in inventory_lines.mapped("product_id")
            ]
            wiz = self.env["stock.track.confirmation"].create(
                {"inventory_id": self.id, "tracking_line_ids": wiz_lines}
            )
            return {
                "name": _("Tracked Products in Inventory Adjustment"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "stock.track.confirmation",
                "target": "new",
                "res_id": wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True

# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one(default=lambda self: self.env.company)

    def write(self, vals):
        # Convert standard type/tracking warnings to blocking errors:
        if "type" in vals:
            has_moves = self.product_variant_ids.ids and self.env[
                "stock.move.line"
            ].sudo().search_count(
                [
                    ("product_id", "in", self.product_variant_ids.ids),
                    ("state", "!=", "cancel"),
                ]
            )
            if has_moves:
                raise ValidationError(
                    _(
                        "This product has been used in at least one inventory movement. "
                        "It is not advised to change the Product Type since it can lead "
                        "to inconsistencies. A better solution could be to archive the "
                        "product and create a new one instead.",
                    )
                )
        new_tracking = vals.get("tracking")
        if new_tracking and new_tracking != "none":
            unassigned_quants = self.env["stock.quant"].search_count(
                [
                    ("product_id", "in", self.product_variant_ids.ids),
                    ("lot_id", "=", False),
                    ("location_id.usage", "=", "internal"),
                ]
            )
            if unassigned_quants:
                raise ValidationError(
                    _(
                        "You have product(s) in stock that have no lot/serial number. "
                        "You can assign lot/serial numbers by doing an inventory adjustment.",
                    )
                )
        return super().write(vals)

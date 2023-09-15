# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one(default=lambda self: self.env.company)

    @api.constrains("type")
    def _check_type(self):
        for rec in self:
            if rec.type == "service":
                has_moves = rec.product_variant_ids.ids and self.env[
                    "stock.move"
                ].search_count(
                    [
                        ("product_id", "in", rec.product_variant_ids.ids),
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

    @api.constrains("tracking")
    def _check_tracking(self):
        for rec in self:
            has_moves = rec.product_variant_ids.ids and self.env[
                "stock.move.line"
            ].sudo().search_count(
                [
                    ("product_id", "in", rec.product_variant_ids.ids),
                    ("state", "!=", "cancel"),
                ]
            )
            if has_moves:
                raise ValidationError(
                    _(
                        "This product has been used in at least one inventory movement. "
                        "It is not advised to change the Tracking type since it can lead "
                        "to inconsistencies. A better solution could be to archive the "
                        "product and create a new one instead.",
                    )
                )

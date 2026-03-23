# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_rental_picking = fields.Boolean(
        compute="_compute_is_rental_picking",
    )

    rental_require_signature_validation = fields.Boolean(
        related="company_id.rental_require_signature_validation",
    )

    @api.depends("sale_id.type_id")
    def _compute_is_rental_picking(self):
        rental_type = self.env.ref(
            "rental_base.rental_sale_type", raise_if_not_found=False
        )
        for picking in self:
            picking.is_rental_picking = bool(
                rental_type
                and picking.sale_id
                and picking.sale_id.type_id == rental_type
            )

    def _attach_sign(self):
        res = super()._attach_sign()
        if (
            self.is_rental_picking
            and self.company_id.rental_require_signature_validation
            and self.state != "done"
        ):
            self.with_context(
                skip_immediate=True,
                skip_backorder=True,
            ).button_validate()
        return res

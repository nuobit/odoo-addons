# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_rental_picking = fields.Boolean(
        compute="_compute_is_rental_picking",
    )

    def _compute_is_rental_picking(self):
        rental_type = self.env.ref(
            "rental_base.rental_sale_type", raise_if_not_found=False
        )
        for picking in self:
            picking.is_rental_picking = (
                rental_type and picking.sale_id.type_id == rental_type
            )

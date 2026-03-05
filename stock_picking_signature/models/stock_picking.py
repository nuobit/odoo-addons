# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    require_signature = fields.Boolean(
        related="picking_type_id.require_signature",
    )
    signed_by = fields.Char(
        copy=False,
    )
    signed_on = fields.Datetime(
        copy=False,
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("signature"):
            now = fields.Datetime.now()
            for picking in self:
                sign_vals = {}
                if not picking.signed_by and picking.partner_id:
                    sign_vals["signed_by"] = picking.partner_id.name
                if not picking.signed_on:
                    sign_vals["signed_on"] = now
                if sign_vals:
                    super(StockPicking, picking).write(sign_vals)
        return res

    def button_validate(self):
        pickings_require_sign = self.filtered(
            lambda p: p.require_signature and not p.signature
        )
        if pickings_require_sign:
            raise UserError(
                _(
                    "The following transfers require a signature"
                    " before validation:\n%s",
                    "\n".join(pickings_require_sign.mapped("name")),
                )
            )
        return super().button_validate()

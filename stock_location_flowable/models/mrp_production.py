# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    picking_id = fields.Many2one(comodel_name="stock.picking")
    production_blocked = fields.Boolean(compute="_compute_production_blocked")
    production_flowable = fields.Boolean(compute="_compute_production_flowable")

    def _compute_production_flowable(self):
        for rec in self:
            rec.production_flowable = rec.picking_type_id.flowable_operation

    def _compute_production_blocked(self):
        for rec in self:
            rec.production_blocked = bool(
                self.env["stock.location"].search_count(
                    [("flowable_production_id", "=", rec.id)]
                )
            )

    @api.constrains("product_id", "move_raw_ids", "location_dest_id")
    def _check_production_lines(self):
        for rec in self:
            if not rec.picking_type_id.flowable_operation:
                super(MrpProduction, rec)._check_production_lines()

    @api.constrains("state")
    def _check_flowable_blocked(self):
        for rec in self:
            if rec.state == "cancel" and rec.picking_id:
                raise ValidationError(
                    _(
                        "You cannot cancel a production with a picking associated."
                        " The mixing is in progress."
                    )
                )

    def write(self, vals):
        for rec in self:
            if (
                rec.picking_id
                and rec.picking_type_id.flowable_operation
                and rec.state == "to_close"
            ):
                raise ValidationError(
                    _(
                        "You cannot modify a mix production with a picking associated."
                        " The mixing is in progress."
                    )
                )
        return super().write(vals)

    def button_mark_done(self):
        res = super().button_mark_done()
        for rec in self:
            if rec.picking_type_id.flowable_operation and rec.state == "done":
                rec._check_flowable_post_production_quants()
        return res

    def _check_flowable_post_production_quants(self):
        """Defensive check — should not be necessary under normal operation
        and might be removed in the future. After completing a mixing order,
        all raw-material lots at the flowable location must have 0 stock —
        only the producing lot should remain. Rounding residuals or manual
        inventory adjustments could leave non-zero leftovers that silently
        corrupt stock. Fail loudly so the issue is caught immediately."""
        self.ensure_one()
        location = self.location_src_id
        rounding = self.product_uom_id.rounding
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("location_id", "=", location.id),
                ("lot_id", "!=", self.lot_producing_id.id),
                ("company_id", "=", self.company_id.id),
            ]
        )
        for quant in quants:
            if not float_is_zero(quant.quantity, precision_rounding=rounding):
                raise ValidationError(
                    _(
                        "After completing the mixing order '%s' at"
                        " flowable location '%s', lot '%s' still has"
                        " %s %s of stock. Expected 0 after merging"
                        " all raw materials into lot '%s'.",
                        self.name,
                        location.name,
                        quant.lot_id.name,
                        quant.quantity,
                        self.product_uom_id.name,
                        self.lot_producing_id.name,
                    )
                )

    def action_assign(self):
        res = super().action_assign()
        for rec in self:
            if rec.picking_type_id.flowable_operation and rec.state not in (
                "to_close",
                "done",
                "cancel",
            ):
                rec._check_flowable_reservation()
        return res

    def _check_flowable_reservation(self):
        self.ensure_one()
        if all(m.state == "assigned" for m in self.move_raw_ids):
            return
        location = self.location_src_id
        reserved_move_lines = self.env["stock.move.line"].search(
            [
                ("location_id", "=", location.id),
                ("product_uom_qty", ">", 0),
                ("state", "not in", ("done", "cancel", "draft")),
                ("move_id.raw_material_production_id", "!=", self.id),
            ]
        )
        if reserved_move_lines:
            details = []
            for ml in reserved_move_lines:
                move = ml.move_id
                if move.picking_id:
                    origin = "%s (%s)" % (
                        move.picking_id.name,
                        move.picking_id.picking_type_id.name,
                    )
                elif move.raw_material_production_id:
                    origin = "%s (%s)" % (
                        move.raw_material_production_id.name,
                        move.raw_material_production_id.picking_type_id.name,
                    )
                else:
                    origin = _("Unknown origin (move %s)", move.id)
                details.append(
                    "  - %s: %s %s (lot %s) - %s"
                    % (
                        ml.product_id.display_name,
                        ml.product_uom_qty,
                        ml.product_uom_id.name,
                        ml.lot_id.name or _("no lot"),
                        origin,
                    )
                )
            raise UserError(
                _(
                    "Cannot merge at flowable location '%s'"
                    " because there are reserved quantities."
                    " After the merge, the current lot(s) will"
                    " have 0 stock and these reservations will"
                    " become invalid.\n\n"
                    "The following operations must be unreserved"
                    " or completed first:\n\n%s",
                    location.name,
                    "\n".join(details),
                )
            )
        raise UserError(
            _(
                "Cannot fully reserve the mixing order at"
                " flowable location '%s'. Raw materials are"
                " in state '%s'.",
                location.name,
                ", ".join(self.move_raw_ids.mapped("state")),
            )
        )

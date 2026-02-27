# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


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

    def action_assign(self):
        res = super().action_assign()
        for rec in self:
            if rec.picking_type_id.flowable_operation:
                rec._check_flowable_reservation()
        return res

    def _check_flowable_reservation(self):
        """Verify that action_assign() fully reserved all raw materials.

        A flowable merge requires 100% of the location's stock. If another
        operation (sale, internal transfer) holds a reservation, action_assign
        cannot fully reserve and the location won't be blocked — leaving it
        unprotected for concurrent receptions. This post-check detects partial
        reservation and rolls back the entire transaction with a clear error
        listing who holds the conflicting reservations.
        """
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
                raise UserError(
                    _(
                        "Move '%s' (id=%s) at flowable"
                        " location '%s' has reserved"
                        " quantities but no picking or"
                        " production associated"
                    )
                    % (move.name, move.id, location.name)
                )
            details.append(
                "  - %s: %s %s — %s"
                % (
                    ml.product_id.display_name,
                    ml.product_uom_qty,
                    ml.product_uom_id.name,
                    origin,
                )
            )
        raise UserError(
            _(
                "Cannot fully reserve flowable location '%s'"
                " because there are other reserved quantities."
                " All stock must be available before merging.\n\n"
                "The following operations have reservations"
                " that must be unreserved first:\n\n%s"
            )
            % (location.name, "\n".join(details))
        )

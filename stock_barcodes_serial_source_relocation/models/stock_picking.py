# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class Picking(models.Model):
    _inherit = "stock.picking"

    def _prepare_relocation_move_line_values(self, move_line, new_picking, quant):
        return {
            "picking_id": new_picking.id,
            "product_id": move_line.product_id.id,
            "origin": self.name,
            "product_uom_id": move_line.product_id.uom_id.id,
            "quantity": quant.quantity,
            "location_id": quant.location_id.id,
            "location_dest_id": move_line.location_id.id,
            "lot_id": move_line.lot_id.id,
        }

    def _prepare_relocation_move_values(self, move_line, quant):
        return {
            "name": self.name,
            "origin": self.name,
            "company_id": self.company_id.id,
            "product_id": move_line.product_id.id,
            "product_uom": move_line.product_id.uom_id.id,
            "product_uom_qty": quant.quantity,
            "quantity": quant.quantity,
            "location_id": quant.location_id.id,
            "location_dest_id": move_line.location_id.id,
        }

    def _prepare_relocation_picking_values(self, move_line, new_picking_type, quant):
        return {
            "picking_type_id": new_picking_type.id,
            "location_id": quant.location_id.id,
            "location_dest_id": move_line.location_id.id,
            "origin": move_line.picking_id.name,
            "company_id": move_line.company_id.id,
            "move_ids": [
                (
                    0,
                    0,
                    self._prepare_relocation_move_values(move_line, quant),
                )
            ],
        }

    def _create_inventory_adjustment(self, move_line):
        quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", move_line.location_id.id),
                ("product_id", "=", move_line.product_id.id),
                ("lot_id", "=", move_line.lot_id.id),
                ("company_id", "=", self.company_id.id),
            ],
            limit=1,
        )

        if not quant:
            quant = self.env["stock.quant"].create(
                {
                    "location_id": move_line.location_id.id,
                    "product_id": move_line.product_id.id,
                    "lot_id": move_line.lot_id.id,
                    "company_id": self.company_id.id,
                    "quantity": 0,
                }
            )

        quant.inventory_quantity_set = True
        quant.inventory_quantity = 1
        quant.with_context(
            inventory_mode=True, relocation_origin=self.name
        ).action_apply_inventory()

    def button_validate(self):
        res = super().button_validate()
        if (
            self.picking_type_code != "incoming"
            and not self.picking_type_id.barcode_option_group_id.allow_negative_quant
        ):
            for move_line in self.move_line_ids.filtered(
                lambda x: x.product_id.tracking == "serial"
                and x.barcode_relocation_scanned
                and x.lot_id
            ):
                quants = move_line.lot_id.quant_ids.filtered(
                    lambda q, ml=move_line: float_compare(
                        q.quantity,
                        0,
                        precision_rounding=ml.product_id.uom_id.rounding,
                    )
                    > 0
                )
                if len(quants) > 1:
                    raise ValidationError(
                        _(
                            "S/N %(name)s is found in more than one location.",
                            name=move_line.lot_id.name,
                        )
                    )
                if quants:
                    qty_available = quants.filtered(
                        lambda x, ml=move_line: x.location_id == ml.location_id
                    ).quantity
                    if (
                        float_compare(
                            move_line.quantity,
                            qty_available,
                            precision_rounding=move_line.product_id.uom_id.rounding,
                        )
                        > 0
                    ):
                        warehouse = move_line.location_id.warehouse_id
                        picking_type = (
                            self.env["stock.picking.type"]
                            .search(
                                [
                                    ("warehouse_id", "in", (warehouse.id, False)),
                                    ("code", "=", "internal"),
                                    ("is_regularization", "=", True),
                                ],
                            )
                            .sorted(lambda x: x.warehouse_id, reverse=True)
                        )
                        warehouse_ids = [pt.warehouse_id.id for pt in picking_type]
                        if len(warehouse_ids) != len(set(warehouse_ids)):
                            raise ValidationError(
                                _(
                                    "More than one regularization picking "
                                    "type for the same warehouse %(warehouse)s",
                                    warehouse=move_line.location_id.name,
                                )
                            )
                        if not picking_type:
                            raise ValidationError(
                                _(
                                    "No regularization picking "
                                    "type for location %(location)s",
                                    location=move_line.location_id.name,
                                )
                            )
                        new_picking = self.env["stock.picking"].create(
                            self._prepare_relocation_picking_values(
                                move_line, picking_type[0], quants
                            )
                        )
                        new_picking.with_context(relocation=self.name).action_confirm()
                        for move in new_picking.move_ids:
                            move.move_line_ids.write(
                                self._prepare_relocation_move_line_values(
                                    move_line, new_picking, quants
                                )
                            )
                        new_picking.button_validate()
                else:
                    self._create_inventory_adjustment(move_line)
        return res

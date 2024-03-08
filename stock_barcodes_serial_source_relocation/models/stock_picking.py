# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
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
            "qty_done": quant.quantity,
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
            "quantity_done": quant.quantity,
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
            "move_lines": [
                (
                    0,
                    0,
                    self._prepare_relocation_move_values(move_line, quant),
                )
            ],
        }

    def _prepare_relocation_inventory_line_values(self, move_line):
        return {
            "location_id": move_line.location_id.id,
            "product_id": move_line.product_id.id,
            "product_uom_id": move_line.product_id.uom_id.id,
            "product_qty": 1,
            "prod_lot_id": move_line.lot_id.id,
            "company_id": self.company_id.id,
        }

    def _prepare_relocation_inventory_values(self, move_line):
        return {
            "name": "Regularization by relocation",
            "product_ids": [(6, 0, move_line.product_id.ids)],
            "location_ids": [(6, 0, move_line.location_id.ids)],
            "exhausted": True,
            "line_ids": [
                (
                    0,
                    0,
                    self._prepare_relocation_inventory_line_values(move_line),
                )
            ],
        }

    def button_validate(self):
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
                    lambda q: float_compare(
                        q.quantity,
                        0,
                        precision_rounding=move_line.product_id.uom_id.rounding,
                    )
                    > 0
                )
                if len(quants) > 1:
                    raise ValidationError(
                        _(
                            "S/N %s is found in more than one location."
                            % move_line.lot_id.name
                        )
                    )
                if quants:
                    qty_available = quants.filtered(
                        lambda x: x.location_id == move_line.location_id
                    ).quantity
                    if (
                        float_compare(
                            move_line.qty_done,
                            qty_available,
                            precision_rounding=move_line.product_id.uom_id.rounding,
                        )
                        > 0
                    ):
                        warehouse = move_line.location_id.get_warehouse()
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
                                    "type for the same warehouse %s"
                                    % move_line.location_id.name
                                )
                            )
                        if not picking_type:
                            raise ValidationError(
                                _(
                                    "No regularization picking type for location %s"
                                    % move_line.location_id.name
                                )
                            )
                        new_picking = self.env["stock.picking"].create(
                            self._prepare_relocation_picking_values(
                                move_line, picking_type[0], quants
                            )
                        )
                        new_picking.action_confirm()
                        for move in new_picking.move_lines:
                            move.move_line_ids.write(
                                self._prepare_relocation_move_line_values(
                                    move_line, new_picking, quants
                                )
                            )
                        new_picking.button_validate()
                else:
                    inventory = self.env["stock.inventory"].create(
                        self._prepare_relocation_inventory_values(move_line)
                    )
                    inventory._action_start()
                    inventory.with_context(
                        relocation_origin=self.name
                    ).action_validate()
        return super().button_validate()

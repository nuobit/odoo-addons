# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"

    @api.model
    def _get_picking_line_labels(self, ml):
        # a receipt line bought in a dynamic unit prints one label per unit it
        # brings; any other line, a return included, prints as the base module
        # does
        if not ml.move_id.is_dynamic_receipt:
            return super()._get_picking_line_labels(ml)

        moves = self.env["stock.move"].search(
            [
                ("picking_id", "=", ml.move_id.picking_id.id),
                ("purchase_line_id", "=", ml.move_id.purchase_line_id.id),
                ("state", "=", "done"),
            ]
        )
        # the lines may be in different units: each is converted to the
        # product's without rounding, since quantity_product_uom is rounded
        # line by line
        quantities = {
            line: line.product_uom_id._compute_quantity(
                line.quantity, line.product_id.uom_id, round=False
            )
            for line in moves.move_line_ids
        }
        total_po_moves_qty = sum(quantities.values())
        # the receipt shares what it received among the units it brings; a
        # receipt done before this module records none
        units_received = sum(moves.mapped("purchase_uom_qty"))
        if units_received == 0:
            raise UserError(
                _(
                    "The receipt has no purchase units received of the product "
                    "%(product)s to share the quantity received among. Unlock it "
                    "(Lock/Unlock) and enter them on the product's line."
                )
                % {"product": ml.product_id.display_name}
            )
        uom_po_ratio = total_po_moves_qty / units_received
        # the line holds a whole number of the units received, and each label
        # carries one of them, both at the precision of the product's unit
        rounding = ml.product_id.uom_id.rounding
        expand_qty = round(quantities[ml] / uom_po_ratio)
        # a line that holds no whole unit would print no label at all; it may
        # read as none at the precision of the product's unit, so it names its
        # own quantity
        if expand_qty == 0:
            raise UserError(
                _(
                    "A line of the receipt holds %(quantity)s %(uom)s of the product "
                    "%(product)s, less than one of its units received. Correct it."
                )
                % {
                    "quantity": ml.quantity,
                    "uom": ml.product_uom_id.name,
                    "product": ml.product_id.display_name,
                }
            )
        if float_compare(
            expand_qty * uom_po_ratio,
            quantities[ml],
            precision_rounding=rounding,
        ):
            raise UserError(
                _(
                    "A line of the receipt holds %(quantity)s %(uom)s of the product "
                    "%(product)s, which is not a multiple of %(share)s %(uom)s, the "
                    "quantity of each unit received. Correct it."
                )
                % {
                    "quantity": float_round(
                        quantities[ml], precision_rounding=rounding
                    ),
                    "uom": ml.product_id.uom_id.name,
                    "product": ml.product_id.display_name,
                    "share": float_round(uom_po_ratio, precision_rounding=rounding),
                }
            )
        # and the lines together hold the units received: a part of a unit in
        # each line can round up to a whole one at that precision
        units_held = sum(
            round(quantity / uom_po_ratio) for quantity in quantities.values()
        )
        if units_held != units_received:
            raise UserError(
                _(
                    "The lines of the receipt hold %(units_held)s units of %(share)s "
                    "%(uom)s of the product %(product)s, but %(units_received)s "
                    "purchase units were received. Correct them."
                )
                % {
                    "units_held": units_held,
                    "share": float_round(uom_po_ratio, precision_rounding=rounding),
                    "uom": ml.product_id.uom_id.name,
                    "product": ml.product_id.display_name,
                    "units_received": units_received,
                }
            )
        # each label carries one unit received: its quantity in the product's
        # unit when that is a weight unit, and otherwise the weight of what it
        # holds, in the unit of the products' weight field (kg, or lb). That
        # weight is the base module's weight of a line, none without a product
        # weight; its share is not rounded to the product's unit, so that the
        # labels add up to the weight received
        if ml.product_uom_category_id == self.env.ref("uom.product_uom_categ_kgm"):
            return (
                expand_qty,
                ml.product_id.uom_id,
                float_round(uom_po_ratio, precision_rounding=rounding),
            )
        return (
            expand_qty,
            self.env["product.template"]._get_weight_uom_id_from_ir_config_parameter(),
            self._get_line_weight(
                ml,
                ml.product_id.uom_id._compute_quantity(
                    uom_po_ratio, ml.product_uom_id, round=False
                ),
            ),
        )

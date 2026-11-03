# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"

    @api.model
    def _get_picking_line_labels(self, ml):
        # compute po uom qty prorated for rhe current move line
        uom_po = ml.move_id.purchase_line_id.product_uom
        if not uom_po.dynamic_ratio:
            return super()._get_picking_line_labels(ml)
        weight_uom = self.env.ref("uom.product_uom_categ_kgm")
        # the unit of the products' weight field: kg, or lb when so configured
        product_weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

        expand_qty = 1
        qty_per_doc = ml.quantity * ml.product_id.weight
        uom_po_ratio = 1
        all_move_lines = (
            self.env["stock.move"]
            .search(
                [
                    ("picking_id", "=", ml.move_id.picking_id.id),
                    ("purchase_line_id", "=", ml.move_id.purchase_line_id.id),
                    ("state", "=", "done"),
                ]
            )
            .move_line_ids
        )
        if len(all_move_lines.product_uom_id) != 1:
            raise UserError(
                _(
                    "All the lines must have the same UoM category "
                    "in a picking to print labels. "
                    "The line with the product: %(product)s has "
                    "multiple lots with different units of measure"
                )
                % {"product": ml.move_id.product_id.display_name}
            )
        total_po_moves_qty = sum(all_move_lines.mapped("quantity"))
        uom_po_qty = ml.move_id.purchase_line_id.product_uom_qty
        if uom_po_qty > 0:
            uom_po_ratio = total_po_moves_qty / uom_po_qty
        if ml.quantity % uom_po_ratio:
            raise UserError(
                _(
                    "The quantity of the product %(product)s"
                    " in the picking line is not a multiple "
                    "of the weight unit of measure %(uom_ratio)s. "
                    "Please correct it."
                )
                % {
                    "product": ml.product_id.display_name,
                    "uom_ratio": uom_po_ratio,
                }
            )
        uom_po_qty = ml.quantity / uom_po_ratio
        expand_qty = uom_po_qty
        if ml.product_uom_category_id == weight_uom:
            qty_per_doc = uom_po_ratio

        # a line in a weight unit carries its own quantity; any other
        # line carries the weight of its product
        uom = (
            ml.product_uom_id
            if ml.product_uom_category_id == weight_uom
            else product_weight_uom
        )
        return int(expand_qty), uom, qty_per_doc

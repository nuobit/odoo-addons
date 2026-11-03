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
        # compute po uom qty prorated for rhe current move line
        uom_po = ml.move_id.purchase_line_id.product_uom
        if not uom_po.dynamic_ratio:
            return super()._get_picking_line_labels(ml)
        weight_uom = self.env.ref("uom.product_uom_categ_kgm")
        # the unit of the products' weight field: kg, or lb when so configured
        product_weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

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
        # the lines may be in different units: each is converted to the
        # product's without rounding, since quantity_product_uom is rounded
        # line by line
        quantities = {
            line: line.product_uom_id._compute_quantity(
                line.quantity, line.product_id.uom_id, round=False
            )
            for line in all_move_lines
        }
        total_po_moves_qty = sum(quantities.values())
        uom_po_qty = ml.move_id.purchase_line_id.product_qty
        if uom_po_qty > 0:
            uom_po_ratio = total_po_moves_qty / uom_po_qty
        # the line holds a whole number of the units bought, and each label
        # carries one of them, both at the precision of the product's unit
        rounding = ml.product_id.uom_id.rounding
        expand_qty = round(quantities[ml] / uom_po_ratio)
        if float_compare(
            expand_qty * uom_po_ratio,
            quantities[ml],
            precision_rounding=rounding,
        ):
            raise UserError(
                _(
                    "The quantity of the product %(product)s"
                    " in the picking line is not a multiple "
                    "of %(uom_ratio)s, the quantity of each unit bought. "
                    "Please correct it."
                )
                % {
                    "product": ml.product_id.display_name,
                    "uom_ratio": float_round(uom_po_ratio, precision_rounding=rounding),
                }
            )
        # each label carries one unit bought: its quantity when the line is
        # in a weight unit, and the weight of what it holds otherwise
        if ml.product_uom_category_id == weight_uom:
            qty_per_doc = float_round(uom_po_ratio, precision_rounding=rounding)
        else:
            qty_per_doc = float_round(
                uom_po_ratio * ml.product_id.weight,
                precision_digits=self.env["decimal.precision"].precision_get(
                    "Stock Weight"
                ),
            )

        # a line in a weight unit carries its quantity in the product's unit;
        # any other line carries the weight of its product
        uom = (
            ml.product_id.uom_id
            if ml.product_uom_category_id == weight_uom
            else product_weight_uom
        )
        return int(expand_qty), uom, qty_per_doc

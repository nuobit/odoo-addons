# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"
    _description = "Report GS1 Barcode"

    # byproduct_ids = fields.One2many('mrp.production', 'move_byproduct_ids')

    @property
    def GS1_AI_FORMAT(self):
        return {
            **super().GS1_AI_FORMAT,
            "3100": (20, False),
        }

    @api.model
    def _prepare_mrp_production_values(self, params):
        model, ids = params["model"], params["ids"]
        unit_uom = self.env.ref("uom.product_uom_categ_unit")
        docs = []
        qty_tracking = {}

        for ml in (
            self.env[model]
            .browse(ids)
            .mapped("move_byproduct_ids")
            .mapped("move_line_ids")
        ):
            product = ml.product_id
            lot = ml.lot_id or None
            uom_cat = ml.product_uom_category_id

            qty_tracking.setdefault(product, {}).setdefault(
                lot,
                {
                    "qty": 0,
                    "uom_category": uom_cat,
                },
            )

            qty_tracking[product][lot]["qty"] += ml.quantity

            if qty_tracking[product][lot]["uom_category"] != uom_cat:
                raise UserError(
                    _(
                        "All lines must have the same UoM category "
                        "in a production to print labels. "
                        "Lot %(lot)s has different UoM categories: "
                        "%(uom1)s and %(uom2)s."
                    )
                    % {
                        "lot": lot.name or "",
                        "uom1": qty_tracking[product][lot]["uom_category"].name,
                        "uom2": uom_cat.name,
                    }
                )

        for product, lots_data in sorted(
            qty_tracking.items(), key=lambda x: x[0].default_code or ""
        ):
            for lot, lot_data in sorted(
                lots_data.items(), key=lambda x: x[0].name if x[0] else ""
            ):
                if lot_data["qty"] > 0:
                    expand_qty = 1
                    if lot_data["uom_category"] == unit_uom:
                        expand_qty = int(lot_data["qty"])
                    docs += [
                        {
                            "product": product,
                            "lot": lot,
                        }
                    ] * expand_qty
        return docs

    @api.model
    def _prepare_gs1_values(self, data):
        res = super()._prepare_gs1_values(data)
        weight = data.get("product", None).weight
        if weight:
            res["3100"] = f"{int(weight)}"
        return res

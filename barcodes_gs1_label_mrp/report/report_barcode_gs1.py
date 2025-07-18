# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"
    _description = "Report GS1 Barcode"

    @api.model
    def _prepare_mrp_production_values(self, params):
        unit_uom = self.env.ref("uom.product_uom_categ_unit")
        model, ids = params["model"], params["ids"]
        docs = []
        for ml in (
            self.env[model]
            .browse(ids)
            .move_byproduct_ids.move_line_ids.sorted(
                lambda x: (x.product_id.default_code or "", x.lot_id.name or "")
            )
        ):
            if ml.quantity > 0:
                expand_qty = 1
                if ml.product_uom_category_id == unit_uom:
                    expand_qty = int(ml.quantity)
                docs += [
                    {
                        "product": ml.product_id,
                        "lot": ml.lot_id,
                        "uom": ml.product_uom_id,
                        "qty": ml.quantity,
                    }
                ] * expand_qty
        return docs

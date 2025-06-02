# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"
    _description = "Report GS1 Barcode"

    @property
    def GS1_AI_FORMAT(self):
        return {
            **super().GS1_AI_FORMAT,
            "3100": (20, False),
        }

    @api.model
    def _prepare_gs1_values(self, product, lot):
        res = super()._prepare_gs1_values(product, lot)
        if self.env.context.get("active_model") == "stock.picking":
            if product.weight:
                weight = int(product.weight)
                res["3100"] = f"{weight}"
        return res

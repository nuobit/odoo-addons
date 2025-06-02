# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
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
    def _prepare_gs1_values(self, data):
        res = super()._prepare_gs1_values(data)
        weight = data.get("weight", None)
        if weight:
            res["3100"] = f"{int(weight)}"
        return res

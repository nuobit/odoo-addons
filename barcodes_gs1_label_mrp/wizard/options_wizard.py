# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class BarcodesGS1PrintOptionsWizard(models.TransientModel):
    _inherit = "barcodes.gs1.label.options.wizard"

    @property
    def MAP_MODEL_REPORT(self):
        return {
            **super().MAP_MODEL_REPORT,
            "mrp.production": (
                "barcodes_gs1_label_mrp.action_report_mrp_production_gs1_barcodes",
            ),
        }

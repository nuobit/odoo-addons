# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ReportGS1Barcode(models.AbstractModel):
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"
    _description = "Report GS1 Barcode"

    @property
    def GS1_AI_FORMAT(self):
        return {
            **super().GS1_AI_FORMAT,
            "17": (6, False),
        }

    @api.model
    def _prepare_gs1_values(self, lot):
        res = super()._prepare_gs1_values(lot)
        if lot.product_id.tracking == "serial":
            if lot.product_id.use_expiration_date:
                if lot.removal_date:
                    date = fields.Datetime.context_timestamp(self, lot.removal_date)
                    res["17"] = date.strftime("%y%m%d")
        return res

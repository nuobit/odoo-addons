# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class ReportBarcodeLabelTemplate(models.AbstractModel):
    _name = "report.barcode_label_template.report_label_template"
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"

    def _get_report_values(self, docids, data=None):
        docs = []
        for doc in data["active_ids"]:
            lot = self.env["stock.production.lot"].browse(doc).exists()
            gs1_barcode = self._prepare_gs1_values(lot.product_id, lot)
            if not gs1_barcode:
                continue
            docs.append(
                {
                    "product": lot.product_id,
                    "barcode_values": gs1_barcode,
                    "barcode_string": self._get_gs1_barcode_string(
                        gs1_barcode, "gs1-datamatrix"
                    ),
                }
            )
        return {
            "docs": docs,
            "barcode_type": data["barcode_type"],
            "position_x": data["position_x"],
            "position_y": data["position_y"],
            "width": data["width"],
        }

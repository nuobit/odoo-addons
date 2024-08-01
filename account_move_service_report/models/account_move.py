# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def prepare_invoice_service(self, vals):
        res = super().prepare_invoice_service(vals)
        if res:
            report_name = "account_move_service_report.report_detailed_xlsx"
            data = vals.get("invoice_line_ids").append({"report_type": "xlsx"})
            iar = self.env["ir.actions.report"]
            report = iar._get_report_from_name(report_name)._render_xlsx(
                self.ids, data=data
            )
            self.env["ir.attachment"].create(
                {
                    "name": "%s-Detailed-Invoice-Service.xlsx" % self.name,
                    "type": "binary",
                    "datas": base64.b64encode(report[0]),
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
        return res

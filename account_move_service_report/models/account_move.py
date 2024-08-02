# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def print_report_invoice_service(self):
        self.ensure_one()
        if not self.partner_id.service_intermediary:
            raise ValidationError(
                _("The partner is not a service intermediary, the report cannot be generated.")
            )
        report_name = "account_move_service_report.report_detailed_xlsx"
        iar = self.env["ir.actions.report"]
        report = iar._get_report_from_name(report_name)._render_xlsx(self.ids, data={})
        move_attachments = self.env["ir.attachment"].search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        ).filtered(lambda x: x.name == "%s-Sale-Service.xlsx" % self.name)
        if move_attachments:
            move_attachments.write({"datas": base64.b64encode(report[0])})
        else:
            self.env["ir.attachment"].create(
                {
                    "name": "%s-Sale-Service.xlsx" % self.name,
                    "type": "binary",
                    "datas": base64.b64encode(report[0]),
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
        return {
            "type": "ir.actions.report",
            "report_name": report_name,
            "report_type": "xlsx",
            "context": dict(self.env.context),
        }


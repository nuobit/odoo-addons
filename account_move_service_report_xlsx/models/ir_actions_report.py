# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _render_xlsx(self, docids, data):
        context = data.get("context", {})
        if not context or not context.get("sale_service_report", False):
            return super(ReportAction, self)._render_xlsx(docids, data)

        invoice = self.env["account.move"].browse(docids)
        attachment = self.retrieve_attachment(invoice)
        if not attachment:
            xlsx = super(ReportAction, self)._render_xlsx(docids, data)
            attachment = self.env["ir.attachment"].create(
                {
                    "name": safe_eval(self.attachment, {"object": invoice}),
                    "type": "binary",
                    "datas": base64.b64encode(xlsx[0]),
                    "res_model": invoice._name,
                    "res_id": invoice.id,
                }
            )
        return base64.b64decode(attachment.datas), "xlsx"

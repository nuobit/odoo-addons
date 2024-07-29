# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_facturae_move_attachments(self):
        result = super()._get_facturae_move_attachments()
        if self.facturae and self.partner_id.attach_invoice_as_annex:
            move_attachments = self.env["ir.attachment"].search(
                [("res_id", "in", self.ids), ("res_model", "=", self._name)]
            )
            existing_checksums = {
                self.env["ir.attachment"]._compute_checksum(r["data"]) for r in result
            }
            for attachment in move_attachments:
                checksum = self.env["ir.attachment"]._compute_checksum(attachment.datas)
                if checksum not in existing_checksums:
                    match = re.match(r"^(.*)\.([^.]*)$", attachment.name)
                    if match:
                        description, content_type = match.groups()
                    else:
                        description = attachment.name
                        content_type = attachment.type
                    result.append(
                        {
                            "data": attachment.datas,
                            "content_type": content_type,
                            "encoding": "BASE64",
                            "description": description,
                            "compression": False,
                        }
                    )
        return result

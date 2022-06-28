# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64

from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_facturae_move_attachments(self):
        result = super(AccountMove, self)._get_facturae_move_attachments()
        new_result = []
        for r in result:
            if r["description"] == _("Invoice %s") % self.name:
                if self.partner_id.attach_invoice_as_annex:
                    if self.company_id.report_service_id:
                        action = self.company_id.report_service_id
                        content, content_type = action._render(self.ids)
                        r.update(
                            {
                                "data": base64.b64encode(content),
                                "content_type": content_type,
                            }
                        )
                    new_result.append(r)
            else:
                if (
                    not self.partner_id.attach_invoice_as_annex
                    or not self.partner_id.attach_invoice_only_default_report
                ):
                    new_result.append(r)
        return new_result

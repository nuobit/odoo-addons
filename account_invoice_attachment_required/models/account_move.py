# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        for rec in self:
            if (
                rec.move_type in ("in_invoice", "in_refund")
                and rec.message_binary_attachment_count == 0
            ):
                raise ValidationError(
                    _(
                        "You cannot post an invoice without a file attachment. "
                        "Please attach a document and try again."
                    )
                )
        return super()._post(soft=soft)

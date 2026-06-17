# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def unlink(self):
        Page = self.env["document.page"]
        blocked = self.filtered(
            lambda a: a.res_model == "document.page"
            and a.res_id
            and Page.browse(a.res_id).exists()
        )
        if blocked:
            raise UserError(
                _(
                    "These attachments belong to a document page and cannot be "
                    "deleted:\n%s"
                )
                % "\n".join("- %s" % a.display_name for a in blocked)
            )
        return super().unlink()

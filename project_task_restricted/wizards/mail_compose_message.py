# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self):
        # the full composer: a person reviewed these recipients and sent it
        return super(
            MailComposeMessage,
            self.with_context(restricted_typed_partner_ids=self.partner_ids.ids),
        ).action_send_mail()

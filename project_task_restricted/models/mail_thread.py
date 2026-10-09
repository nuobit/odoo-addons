# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        """Every notification, in the inbox or by e-mail, is decided here,
        whatever posts the message. One about a marked task reaches only the
        recipients the task allows."""
        recipients_data = super()._notify_compute_recipients(message, msg_vals)
        return message._restricted_task()._restricted_filter_recipients(
            message, recipients_data
        )

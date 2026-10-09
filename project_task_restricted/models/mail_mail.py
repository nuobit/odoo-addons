# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import Command, _, api, models, tools

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, vals_list):
        """Every outgoing e-mail is queued here, whatever sends it. One about
        a marked task goes only to the recipients the task allows."""
        mails = super().create(vals_list)
        for mail in mails:
            mail.mail_message_id._restricted_task()._restricted_filter_mail(mail)
        return mails

    @api.model
    def _restricted_split_addresses(self, text, emails):
        """The addresses of a To or Cc text whose e-mail is one of the given
        ones, and how many others it had."""
        addresses = tools.email_split_and_format(text)
        kept = [
            address for address in addresses if tools.email_normalize(address) in emails
        ]
        return kept, len(addresses) - len(kept)

    def _restricted_send_only_to(self, partners):
        """Keep among the recipients of this e-mail only the given partners,
        listed as partners or written as addresses, and cancel it when no
        recipient is left."""
        self.ensure_one()
        emails = {email for email in partners.mapped("email_normalized") if email}
        kept_to, removed_to = self._restricted_split_addresses(self.email_to, emails)
        kept_cc, removed_cc = self._restricted_split_addresses(self.email_cc, emails)
        removed_partners = self.recipient_ids - partners
        if removed_partners or removed_to or removed_cc:
            values = {
                "recipient_ids": [
                    Command.unlink(partner.id) for partner in removed_partners
                ],
                "email_to": ", ".join(kept_to) or False,
                "email_cc": ", ".join(kept_cc) or False,
            }
            # the Cc addresses travel only with a To address or a partner
            if not (self.recipient_ids - removed_partners or kept_to):
                values.update(
                    state="cancel",
                    failure_reason=_(
                        "Not sent: it is about a restricted task, and none of "
                        "its recipients is a member of the Restricted tasks "
                        "group or was addressed on purpose."
                    ),
                )
            self.write(values)
            _logger.info(
                "Mail %s is about a restricted task: %s recipients outside the "
                "Restricted tasks group removed",
                self.id,
                len(removed_partners) + removed_to + removed_cc,
            )

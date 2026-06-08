# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .document_page_history_recipient import NOTIFICATION_STATUS_SELECTION


class DocumentPageHistoryRecipientSend(models.Model):

    _name = "document.page.history.recipient.send"
    _description = "Document Page Distribution Send"
    _order = "sent_date desc, id desc"

    recipient_id = fields.Many2one(
        "document.page.history.recipient",
        required=True,
        ondelete="cascade",
        index=True,
    )
    history_id = fields.Many2one(
        "document.page.history",
        related="recipient_id.history_id",
        store=True,
        index=True,
    )
    document_page_id = fields.Many2one(
        "document.page",
        related="recipient_id.document_page_id",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="recipient_id.company_id",
        store=True,
        index=True,
    )
    sent_date = fields.Datetime()
    sent_by = fields.Many2one("res.users")
    email = fields.Char()
    template_id = fields.Many2one("mail.template")
    mail_message_id = fields.Many2one("mail.message", ondelete="set null")
    mail_notification_id = fields.Many2one("mail.notification", ondelete="set null")
    notification_status = fields.Selection(
        NOTIFICATION_STATUS_SELECTION,
        related="mail_notification_id.notification_status",
        store=True,
    )

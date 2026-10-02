# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumentPageHistoryRecipientSend(models.Model):

    _name = "document.page.history.recipient.send"
    _description = "Document Page Distribution Send"
    _order = "sent_date desc, id desc"

    recipient_id = fields.Many2one(
        comodel_name="document.page.history.recipient",
        required=True,
        ondelete="restrict",
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
    sent_date = fields.Datetime(required=True)
    sent_by_id = fields.Many2one(comodel_name="res.users")
    email = fields.Char()
    template_id = fields.Many2one("mail.template")
    mail_message_id = fields.Many2one("mail.message", ondelete="set null")
    mail_notification_id = fields.Many2one("mail.notification", ondelete="set null")
    notification_status = fields.Selection(
        selection="_selection_notification_status",
        string="Delivery Status",
        compute="_compute_notification_status",
        store=True,
    )

    @api.depends("mail_notification_id.notification_status")
    def _compute_notification_status(self):
        for send in self:
            if send.mail_notification_id:
                send.notification_status = send.mail_notification_id.notification_status
            else:
                # Odoo deletes the notification of a delivered email some time
                # after the send: the send keeps the last status it stored
                send.notification_status = send.notification_status

    @api.model
    def _selection_notification_status(self):
        return self.env["mail.notification"].fields_get(["notification_status"])[
            "notification_status"
        ]["selection"]

# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

NOTIFICATION_STATE_MAP = {
    "ready": "queued",
    "sent": "sent",
    "bounce": "bounce",
    "exception": "error",
    "canceled": "canceled",
}

STATE_SELECTION = [
    ("pending", "Pending"),
    ("no_email", "No email"),
    ("queued", "Queued"),
    ("sent", "Sent"),
    ("error", "Error"),
    ("bounce", "Bounce"),
    ("canceled", "Canceled"),
]

NOTIFICATION_STATUS_SELECTION = [
    ("ready", "Ready to Send"),
    ("sent", "Sent"),
    ("bounce", "Bounced"),
    ("exception", "Exception"),
    ("canceled", "Canceled"),
]


class DocumentPageHistoryRecipient(models.Model):

    _name = "document.page.history.recipient"
    _description = "Document Page Distribution Recipient"
    _rec_name = "partner_id"

    history_id = fields.Many2one(
        "document.page.history",
        required=True,
        ondelete="cascade",
        index=True,
    )
    document_page_id = fields.Many2one(
        "document.page",
        related="history_id.page_id",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="history_id.company_id",
        store=True,
        index=True,
    )
    partner_id = fields.Many2one("res.partner", required=True, index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    email = fields.Char()
    send_ids = fields.One2many(
        "document.page.history.recipient.send",
        "recipient_id",
        string="Sends",
    )
    sent_count = fields.Integer(compute="_compute_send_info")
    last_successful_sent_date = fields.Datetime(
        string="Last send",
        compute="_compute_send_info",
    )
    state = fields.Selection(
        STATE_SELECTION,
        compute="_compute_send_info",
    )

    _sql_constraints = [
        (
            "history_partner_uniq",
            "unique(history_id, partner_id)",
            "A recipient can only appear once per document version.",
        ),
    ]

    @api.depends(
        "email",
        "send_ids.sent_date",
        "send_ids.email",
        "send_ids.notification_status",
    )
    def _compute_send_info(self):
        for rec in self:
            real_sends = rec.send_ids.filtered("sent_date").sorted("sent_date")
            rec.sent_count = len(real_sends)
            last = real_sends[-1:]
            last_ok = real_sends.filtered(lambda s: s.notification_status == "sent")[
                -1:
            ]
            rec.last_successful_sent_date = last_ok.sent_date if last_ok else False
            status = last.notification_status if last else False
            if status:
                rec.state = NOTIFICATION_STATE_MAP.get(status, "queued")
            elif not rec.email:
                rec.state = "no_email"
            else:
                rec.state = "pending"

    def action_open_sends(self):
        self.ensure_one()
        return {
            "name": _("Sends"),
            "type": "ir.actions.act_window",
            "res_model": "document.page.history.recipient.send",
            "view_mode": "tree,form",
            "domain": [("recipient_id", "=", self.id)],
            "target": "new",
        }

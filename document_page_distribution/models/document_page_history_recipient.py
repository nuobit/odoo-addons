# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

NOTIFICATION_STATE_MAP = {
    "ready": "queued",
    "sent": "sent",
    "bounce": "bounce",
    "exception": "error",
    "canceled": "canceled",
}

STATE_SELECTION = [
    ("pending", "Pending"),
    ("no_access", "No access"),
    ("no_email", "No email"),
    ("queued", "Queued"),
    ("sent", "Sent"),
    ("error", "Error"),
    ("bounce", "Bounce"),
    ("canceled", "Canceled"),
]

# states of a recipient whose last send is on its way or has been delivered
SENT_STATES = ("queued", "sent")


class DocumentPageHistoryRecipient(models.Model):

    _name = "document.page.history.recipient"
    _description = "Document Page Distribution Recipient"
    _rec_name = "partner_id"

    history_id = fields.Many2one(
        comodel_name="document.page.history",
        required=True,
        ondelete="restrict",
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
    has_access = fields.Boolean(
        help="The user could read the document when the distribution was confirmed.",
    )
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
        "has_access",
        "send_ids.sent_date",
        "send_ids.email",
        "send_ids.notification_status",
    )
    def _compute_send_info(self):
        for rec in self:
            real_sends = rec.send_ids.sorted("sent_date")
            rec.sent_count = len(real_sends)
            last = real_sends[-1:]
            last_ok = real_sends.filtered(lambda s: s.notification_status == "sent")[
                -1:
            ]
            rec.last_successful_sent_date = last_ok.sent_date if last_ok else False
            if last:
                rec.state = rec._get_state_of_send(last)
            else:
                rec.state = rec._get_state_without_sends(rec.has_access, rec.email)

    @api.model
    def _get_state_of_send(self, send):
        """State of a recipient whose last send is ``send``."""
        status = send.notification_status
        if status not in NOTIFICATION_STATE_MAP:
            raise UserError(
                _(
                    "The distribution log does not know the delivery status "
                    "'%(status)s' of the send to %(email)s. Please contact your "
                    "administrator.",
                    status=status,
                    email=send.email,
                )
            )
        return NOTIFICATION_STATE_MAP[status]

    @api.model
    def _get_state_without_sends(self, has_access, email):
        """State of a user in scope who has not been sent the version."""
        if has_access:
            if email:
                state = "pending"
            else:
                state = "no_email"
        else:
            state = "no_access"
        return state

    @api.model
    def _is_sendable(self, has_access, email):
        return self._get_state_without_sends(has_access, email) == "pending"

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

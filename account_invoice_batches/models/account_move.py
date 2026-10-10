# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from .common import BATCH_SENDING_METHODS


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_batch_id = fields.Many2one(
        comodel_name="account.invoice.batch",
        ondelete="restrict",
        string="Invoice batch",
        tracking=True,
        copy=False,
    )
    invoice_batch_sending_method = fields.Selection(
        selection=BATCH_SENDING_METHODS,
        string="Sending method",
        tracking=True,
    )
    invoice_batch_email_partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain="[('id', 'child_of', partner_id), ('email', '!=', False)]",
        ondelete="restrict",
        string="Contact",
        tracking=True,
    )
    invoice_batch_email_recipient_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_invoice_batch_email_recipient_id",
        string="Batch e-mail recipient",
        help="Recipient of the batch e-mail: the batch e-mail contact of the "
        "invoice or, when it is empty, its partner.",
    )

    @api.depends("invoice_batch_email_partner_id", "partner_id")
    def _compute_invoice_batch_email_recipient_id(self):
        for move in self:
            move.invoice_batch_email_recipient_id = (
                move.invoice_batch_email_partner_id or move.partner_id
            )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id.invoice_batch_sending_method:
            self.invoice_batch_sending_method = (
                self.partner_id.invoice_batch_sending_method
            )
        if self.partner_id.invoice_batch_email_partner_id:
            self.invoice_batch_email_partner_id = (
                self.partner_id.invoice_batch_email_partner_id
            )
        return res

    def _post(self, soft=True):
        # the customer follower added at validation is, on a batch invoice,
        # the batch e-mail contact: see message_subscribe
        return super(
            AccountMove, self.with_context(invoice_batch_swap_billing_follower=True)
        )._post(soft=soft)

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """Subscribe the batch e-mail contact instead of the partner at validation.

        Core subscribes the partner of every posted move, one move at a time.
        Under the flag set by ``_post``, and only for that exact call on a
        batch invoice whose contact differs from the partner, the contact
        takes the partner's place: it is the recipient of the batch e-mail, so
        it is the one whose replies must reach the invoice followers. A partner
        already subscribed by hand stays (core then asks for nobody), an
        archived contact is dropped by core like any other partner, and every
        other call keeps the native behaviour.
        """
        if (
            self.env.context.get("invoice_batch_swap_billing_follower")
            and len(self) == 1
            and self.invoice_batch_id
            and partner_ids == [self.partner_id.id]
            and self.invoice_batch_email_partner_id
            and self.invoice_batch_email_partner_id != self.partner_id
        ):
            partner_ids = [self.invoice_batch_email_partner_id.id]
        return super().message_subscribe(
            partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids
        )

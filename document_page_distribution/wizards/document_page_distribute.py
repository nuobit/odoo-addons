# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.document_page_history_recipient import STATE_SELECTION


class DocumentPageDistribute(models.TransientModel):

    _name = "document.page.distribute"
    _description = "Distribute Document Page"

    document_page_id = fields.Many2one("document.page", required=True, readonly=True)
    history_id = fields.Many2one(
        "document.page.history", string="Version", readonly=True
    )
    template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        required=True,
        domain="[('model', '=', 'document.page')]",
    )
    line_ids = fields.One2many(
        "document.page.distribute.line", "wizard_id", string="Recipients"
    )

    @api.model
    def _preselect(self, recipient):
        if not recipient:
            return True
        return recipient.state not in ("sent", "queued")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        page = self.env["document.page"].browse(
            self.env.context.get("default_document_page_id")
        )
        if not page:
            return res
        page._check_distribution_manager()
        history = page.history_head
        if not history:
            raise UserError(_("This document has no current version to distribute."))
        template = page._get_distribution_template()
        users = page._get_distribution_coverage_users()
        existing = {r.partner_id.id: r for r in history.recipient_ids}
        lines = []
        for user in users:
            partner = user.partner_id
            recipient = existing.get(partner.id)
            sendable = bool(partner.email)
            lines.append(
                (
                    0,
                    0,
                    {
                        "partner_id": partner.id,
                        "user_id": user.id,
                        "email": partner.email,
                        "current_state": recipient.state
                        if recipient
                        else ("pending" if sendable else "no_email"),
                        "sendable": sendable,
                        "selected": sendable and self._preselect(recipient),
                    },
                )
            )
        res.update(
            {
                "document_page_id": page.id,
                "history_id": history.id,
                "template_id": template.id,
                "line_ids": lines,
            }
        )
        return res

    def action_confirm(self):
        self.ensure_one()
        page = self.document_page_id
        page._check_distribution_manager()
        history = page.history_head
        if not history:
            raise UserError(_("This document has no current version to distribute."))
        if history != self.history_id:
            raise UserError(
                _(
                    "The current version of the document has changed. "
                    "Close this window and distribute again."
                )
            )
        users = page._get_distribution_coverage_users()
        recipients = page._ensure_distribution_recipients(history, users)
        selected_partners = self.line_ids.filtered(
            lambda line: line.selected and line.sendable
        ).mapped("partner_id")
        to_send = recipients.filtered(lambda r: r.partner_id in selected_partners)
        if to_send:
            page._distribute_send(history, to_send, self.template_id)
        return {"type": "ir.actions.act_window_close"}


class DocumentPageDistributeLine(models.TransientModel):
    _name = "document.page.distribute.line"
    _description = "Distribute Document Page Line"

    wizard_id = fields.Many2one(
        "document.page.distribute", required=True, ondelete="cascade"
    )
    partner_id = fields.Many2one("res.partner", readonly=True)
    user_id = fields.Many2one("res.users", readonly=True)
    email = fields.Char(readonly=True)
    current_state = fields.Selection(
        STATE_SELECTION, string="Current State", readonly=True
    )
    sendable = fields.Boolean()
    selected = fields.Boolean(string="Send")

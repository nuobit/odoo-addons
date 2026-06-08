# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class DocumentPage(models.Model):
    _inherit = "document.page"

    current_recipient_ids = fields.One2many(
        "document.page.history.recipient",
        related="history_head.recipient_ids",
        string="Current Distribution",
        readonly=True,
    )
    current_distribution_count = fields.Integer(
        compute="_compute_current_distribution_count",
    )

    @api.depends("current_recipient_ids")
    def _compute_current_distribution_count(self):
        for page in self:
            page.current_distribution_count = len(page.current_recipient_ids)

    def _check_distribution_manager(self):
        if not self.env.user.has_group("document_page.group_document_manager"):
            raise AccessError(
                _("Only document managers are allowed to distribute documents.")
            )

    def _get_distribution_groups(self):
        """Security groups of the document (from document_page_access_group)."""
        self.ensure_one()
        return self.groups_id

    def _get_distribution_coverage_users(self):
        """Effective distribution coverage.

        Active internal users (``share=False``) having any of the document
        Security groups within their effective ``groups_id`` (Odoo already
        materializes implied groups), restricted to the users that can access
        the document company, deduplicated by ``partner_id`` (deterministic
        ``user_id`` = lowest id). Empty Security groups block the distribution.
        """
        self.ensure_one()
        groups = self._get_distribution_groups()
        if not groups:
            raise UserError(
                _(
                    "This document has no group defined in Security. "
                    "The distribution coverage cannot be computed."
                )
            )
        users = self.env["res.users"].search(
            [
                ("active", "=", True),
                ("share", "=", False),
                ("groups_id", "in", groups.ids),
            ],
            order="id",
        )
        if self.company_id:
            users = users.filtered(lambda u: self.company_id in u.company_ids)
        seen = set()
        result = self.env["res.users"]
        for user in users:
            if user.partner_id.id not in seen:
                seen.add(user.partner_id.id)
                result |= user
        return result

    def _get_distribution_template(self):
        self.ensure_one()
        company = self.company_id or self.env.company
        template = company.document_page_distribution_template_id
        if not template:
            raise UserError(
                _(
                    "No default distribution template is configured for "
                    "company '%s'. Please configure it in Settings before "
                    "distributing."
                )
                % company.display_name
            )
        return template

    def action_distribute(self):
        self.ensure_one()
        self._check_distribution_manager()
        if not self.history_head:
            raise UserError(_("This document has no current version to distribute."))
        self._get_distribution_coverage_users()
        self._get_distribution_template()
        return {
            "name": _("Distribute Document"),
            "type": "ir.actions.act_window",
            "res_model": "document.page.distribute",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"default_document_page_id": self.id},
        }

    def _ensure_distribution_recipients(self, history, users):
        self.ensure_one()
        Recipient = self.env["document.page.history.recipient"]
        existing = {r.partner_id.id: r for r in history.recipient_ids}
        recipients = Recipient.browse()
        for user in users:
            partner = user.partner_id
            vals = {"email": partner.email, "user_id": user.id}
            rec = existing.get(partner.id)
            if rec:
                rec.write(vals)
            else:
                rec = Recipient.create(
                    dict(vals, history_id=history.id, partner_id=partner.id)
                )
            recipients |= rec
        return recipients

    def _distribution_recipients_data(self, recipients):
        data = []
        for rec in recipients:
            data.append(
                {
                    "id": rec.partner_id.id,
                    "active": True,
                    "share": False,
                    "notif": "email",
                    "type": "user",
                    "groups": rec.user_id.groups_id.ids,
                }
            )
        return data

    def _distribute_send(self, history, recipients, template):
        self.ensure_one()
        self._check_distribution_manager()
        Send = self.env["document.page.history.recipient.send"]
        Recipient = self.env["document.page.history.recipient"]
        sendable = recipients.filtered(lambda r: r.email)
        lang_groups = {}
        for rec in sendable:
            lang = rec.user_id.lang or "en_US"
            lang_groups.setdefault(lang, Recipient.browse())
            lang_groups[lang] |= rec
        now = fields.Datetime.now()
        for lang, recs in lang_groups.items():
            partners = recs.mapped("partner_id")
            subject = template._render_field("subject", [self.id], set_lang=lang)[
                self.id
            ]
            body = template._render_field(
                "body_html", [self.id], set_lang=lang, post_process=True
            )[self.id]
            email_from = template._render_field("email_from", [self.id], set_lang=lang)[
                self.id
            ]
            message = self._message_log(
                body=body,
                subject=subject,
                email_from=email_from or None,
                message_type="notification",
                partner_ids=partners.ids,
            )
            self._notify_record_by_email(
                message,
                {
                    "partners": self._distribution_recipients_data(recs),
                    "channels": [],
                },
                send_after_commit=False,
            )
            notifications = self.env["mail.notification"].search(
                [
                    ("mail_message_id", "=", message.id),
                    ("notification_type", "=", "email"),
                ]
            )
            notif_by_partner = {n.res_partner_id.id: n for n in notifications}
            for rec in recs:
                notif = notif_by_partner.get(rec.partner_id.id)
                Send.create(
                    {
                        "recipient_id": rec.id,
                        "sent_date": now,
                        "sent_by": self.env.user.id,
                        "email": rec.email,
                        "template_id": template.id,
                        "mail_message_id": message.id,
                        "mail_notification_id": notif.id if notif else False,
                    }
                )

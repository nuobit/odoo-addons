# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html as lxml_html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

WEB_CONTENT_PREFIX = "/web/content/"
TRACKING_ROUTE = "/document_page_distribution_download_log/download"


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # rewrite AFTER create: the tracking URL embeds the record id, which
        # does not exist before the INSERT (cannot be a vals transform)
        for record in records:
            record._apply_download_link_tracking()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "content" in vals:
            for record in self:
                record._apply_download_link_tracking()
        return res

    def _apply_download_link_tracking(self):
        self.ensure_one()
        content = self.content or ""
        new_content = self._rewrite_download_links(content)
        if new_content != content:
            # plain self.write() would re-enter the write override above and
            # recurse; call the base write to persist the rewritten content
            super(DocumentPageHistory, self).write({"content": new_content})
        self._bind_tracked_attachment()

    def _bind_tracked_attachment(self):
        self.ensure_one()
        if not self.page_id:
            return
        for attachment_id in self._tracked_attachment_ids(self.content or ""):
            attachment = self.env["ir.attachment"].sudo().browse(attachment_id)
            if (
                attachment.exists()
                and attachment.res_model == "document.page"
                and not attachment.res_id
                and attachment.create_uid.id == self.env.uid
            ):
                attachment.res_id = self.page_id.id

    @staticmethod
    def _leading_int(segment):
        digits = ""
        for char in segment:
            if not char.isdigit():
                break
            digits += char
        return int(digits) if digits else False

    def _download_link_attachment_id(self, href):
        """Attachment id of a ``/web/content`` document link, or ``False``.

        Recognises the URL shapes Odoo emits: ``/web/content/42``,
        ``/web/content/42?download=true``, the slugged
        ``/web/content/42-name.pdf`` and ``/web/content/ir.attachment/42/datas``,
        plus already-tracked controller links. Inline images
        (``/web/image/...``) are not matched. URL parsing only, no regex; the
        PDF restriction is applied separately in :meth:`_is_trackable_pdf`.
        """
        path = (href or "").split("?", 1)[0]
        if path.startswith(TRACKING_ROUTE + "/"):
            parts = path[len(TRACKING_ROUTE) + 1 :].split("/")
            if len(parts) >= 2 and parts[1].isdigit():
                return int(parts[1])
            return False
        if path.startswith(WEB_CONTENT_PREFIX):
            rest = path[len(WEB_CONTENT_PREFIX) :]
            if rest.startswith("ir.attachment/"):
                rest = rest[len("ir.attachment/") :]
            return self._leading_int(rest.split("/", 1)[0])
        return False

    def _is_trackable_pdf(self, attachment_id):
        if not attachment_id:
            return False
        attachment = self.env["ir.attachment"].sudo().browse(attachment_id)
        return attachment.exists() and attachment.mimetype == "application/pdf"

    def _tracked_attachment_ids(self, content):
        if not content or "<a" not in content:
            return set()
        fragment = lxml_html.fragment_fromstring(content, create_parent="div")
        ids = set()
        for anchor in fragment.findall(".//a"):
            attachment_id = self._download_link_attachment_id(anchor.get("href"))
            if self._is_trackable_pdf(attachment_id):
                ids.add(attachment_id)
        return ids

    def _rewrite_download_links(self, content):
        self.ensure_one()
        if not content or "<a" not in content:
            return content
        fragment = lxml_html.fragment_fromstring(content, create_parent="div")
        trackable = [
            anchor
            for anchor in fragment.findall(".//a")
            if self._is_trackable_pdf(
                self._download_link_attachment_id(anchor.get("href"))
            )
        ]
        if len(trackable) > 1:
            raise ValidationError(
                _(
                    "A document version can contain at most one downloadable "
                    "document link."
                )
            )
        if not trackable:
            return content
        anchor = trackable[0]
        href = anchor.get("href") or ""
        attachment_id = self._download_link_attachment_id(href)
        expected = "%s/%s/%s" % (TRACKING_ROUTE, self.id, attachment_id)
        if href.split("?", 1)[0] == expected:
            return content
        anchor.set("href", expected)
        # serialize text + children only: create_parent wrapped the content
        # in an artificial <div> that must not be saved into the document
        return (fragment.text or "") + "".join(
            lxml_html.tostring(child, encoding="unicode") for child in fragment
        )

    def _download_attachment_is_tracked(self, attachment_id):
        self.ensure_one()
        return attachment_id in self._tracked_attachment_ids(self.content or "")

    def _log_recipient_download(
        self, attachment_id, user=None, ip_address=None, user_agent=None
    ):
        self.ensure_one()
        user = user or self.env.user
        download_model = self.env["document.page.history.recipient.download"]
        partner = user.partner_id
        recipient = self.env["document.page.history.recipient"].search(
            [("history_id", "=", self.id), ("partner_id", "=", partner.id)],
            limit=1,
        )
        if not recipient:
            return download_model
        # sudo on create only: the download log is read-only at ACL level
        # (1,0,0,0) -- rows are audit evidence, never user-writable -- so the
        # system appends them on the user's behalf.
        return download_model.sudo().create(
            {
                "recipient_id": recipient.id,
                "user_id": user.id,
                "partner_id": partner.id,
                "attachment_id": attachment_id,
                "download_date": fields.Datetime.now(),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

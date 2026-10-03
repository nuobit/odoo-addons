# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html as lxml_html
from werkzeug.urls import url_encode, url_parse

from odoo import api, fields, models

WEB_CONTENT_PREFIX = "/web/content/"
TRACKING_ROUTE = "/document_page_distribution_download_log/download"


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    # facts of the version, the same for every reader
    download_recipient_count = fields.Integer(
        compute="_compute_download_recipient_count",
        compute_sudo=True,
    )
    download_summary = fields.Char(
        compute="_compute_download_summary",
        compute_sudo=True,
    )

    @api.depends("recipient_ids.downloaded")
    def _compute_download_recipient_count(self):
        for history in self:
            history.download_recipient_count = len(
                history.recipient_ids.filtered("downloaded")
            )

    @api.depends("distribution_count", "download_recipient_count")
    def _compute_download_summary(self):
        for history in self:
            if history.distribution_count:
                history.download_summary = "%s/%s" % (
                    history.download_recipient_count,
                    history.distribution_count,
                )
            else:
                history.download_summary = False

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
        (``/web/image/...``) are not matched. URL parsing only, no regex.
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

    def _tracked_attachment_ids(self, content):
        """Ids of the attachments the anchors of ``content`` link to."""
        if not content or "<a" not in content:
            return set()
        fragment = lxml_html.fragment_fromstring(content, create_parent="div")
        linked_ids = {
            self._download_link_attachment_id(anchor.get("href"))
            for anchor in fragment.findall(".//a")
        }
        linked_ids.discard(False)
        return set(self.env["ir.attachment"].browse(linked_ids).exists().ids)

    def _get_tracking_url(self, attachment_id, href):
        """Address of the tracking route for the link ``href`` to the
        attachment, with the access token of the link when it has one."""
        self.ensure_one()
        url = "%s/%s/%s" % (TRACKING_ROUTE, self.id, attachment_id)
        access_token = url_parse(href).decode_query().get("access_token")
        if access_token:
            url = "%s?%s" % (url, url_encode({"access_token": access_token}))
        return url

    def _rewrite_download_links(self, content):
        self.ensure_one()
        tracked_ids = self._tracked_attachment_ids(content)
        if not tracked_ids:
            return content
        fragment = lxml_html.fragment_fromstring(content, create_parent="div")
        rewritten = False
        for anchor in fragment.findall(".//a"):
            href = anchor.get("href") or ""
            attachment_id = self._download_link_attachment_id(href)
            if attachment_id not in tracked_ids:
                continue
            tracking_url = self._get_tracking_url(attachment_id, href)
            if href != tracking_url:
                anchor.set("href", tracking_url)
                rewritten = True
        if not rewritten:
            return content
        # serialize text + children only: create_parent wrapped the content
        # in an artificial <div> that must not be saved into the document
        return (fragment.text or "") + "".join(
            lxml_html.tostring(child, encoding="unicode") for child in fragment
        )

    def _download_attachment_is_tracked(self, attachment_id):
        self.ensure_one()
        return attachment_id in self._tracked_attachment_ids(self.content or "")

    def _log_recipient_download(self, attachment_id):
        self.ensure_one()
        # no user can write the download log: the module writes the row for
        # the user who downloads the file
        return (
            self.env["document.page.history.recipient.download"]
            .sudo()
            .create(
                {
                    "history_id": self.id,
                    "user_id": self.env.user.id,
                    "attachment_id": attachment_id,
                }
            )
        )

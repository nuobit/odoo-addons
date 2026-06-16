# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import re

from lxml import etree, html

from odoo import api, models
from odoo.osv import expression

POSITIVE_TEXT_OPERATORS = ("like", "ilike", "=like", "=ilike")
ATTACHMENT_URL_RE = re.compile(r"/web/(?:content|image)/(\d+)")


class DocumentPage(models.Model):
    _inherit = "document.page"

    def _linked_attachment_ids(self):
        self.ensure_one()
        if not self.content:
            return set()
        try:
            tree = html.fragment_fromstring(self.content, create_parent=True)
        except (etree.ParserError, ValueError):
            return set()
        linked_ids = set()
        for url in tree.xpath(".//@href | .//@src"):
            match = ATTACHMENT_URL_RE.search(url)
            if match:
                linked_ids.add(int(match.group(1)))
        return linked_ids

    def _search_content(self, operator, value):
        domain = super()._search_content(operator, value)
        if operator not in POSITIVE_TEXT_OPERATORS:
            return domain
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "document.page"),
                ("index_content", operator, value),
            ]
        )
        page_ids = set()
        for attachment in attachments:
            page = self.browse(attachment.res_id).exists()
            if not page:
                continue
            # Odoo keeps the ir.attachment when a file is removed from the
            # editor, so matching by res_id alone would yield stale hits: keep
            # the page only if the attachment is still linked from its HTML.
            if attachment.id in page._linked_attachment_ids():
                page_ids.add(page.id)
        if not page_ids:
            return domain
        return expression.OR([domain, [("id", "in", list(page_ids))]])

    def _anchor_orphan_attachments(self):
        Attachment = self.env["ir.attachment"]
        for page in self:
            linked = page._linked_attachment_ids()
            if not linked:
                continue
            orphans = (
                Attachment.browse(sorted(linked))
                .exists()
                .filtered(lambda a: a.res_model == "document.page" and not a.res_id)
            )
            if orphans:
                orphans.write({"res_id": page.id})

    @api.model_create_multi
    def create(self, vals_list):
        pages = super().create(vals_list)
        pages._anchor_orphan_attachments()
        return pages

    def write(self, vals):
        res = super().write(vals)
        if "content" in vals:
            self._anchor_orphan_attachments()
        return res

    def reindex_linked_attachment_content(self, batch_size=500, only_missing=True):
        """Recompute ``ir.attachment.index_content`` for the attachments linked
        from the page HTML, e.g. after a bulk migration that imported the files
        without indexing them. Reuses Odoo's ``ir.attachment._index`` and never
        writes ``content``, so no page revision is created.

        Called on a recordset it processes those pages; called on the model it
        processes every content page. ``batch_size`` caps how many attachments
        are reindexed per call (re-run until ``processed`` is 0); ``only_missing``
        skips attachments that already have indexed content.

        Returns a summary dict ``{"processed", "skipped", "no_text"}``:
        ``processed`` how many attachments were reindexed, ``skipped`` how many
        were left untouched (already indexed or without data), and ``no_text``
        the ``(id, name)`` of attachments that yielded no extractable text
        (scanned PDFs, or PDFs indexed without ``pdfminer.six``).
        """
        attachment_model = self.env["ir.attachment"]
        pages = self or self.search([("type", "=", "content")])
        processed = 0
        skipped = 0
        no_text = []
        for page in pages:
            if batch_size and processed >= batch_size:
                break
            linked = attachment_model.browse(sorted(page._linked_attachment_ids()))
            for attachment in linked.exists():
                if only_missing and attachment.index_content:
                    skipped += 1
                    continue
                datas = attachment.with_context(bin_size=False).datas
                if not datas:
                    skipped += 1
                    continue
                content = attachment._index(
                    base64.b64decode(datas), attachment.mimetype
                )
                attachment.index_content = content
                processed += 1
                family = (attachment.mimetype or "").split("/")[0]
                if not content or content == family:
                    no_text.append((attachment.id, attachment.name))
                if batch_size and processed >= batch_size:
                    break
        return {"processed": processed, "skipped": skipped, "no_text": no_text}

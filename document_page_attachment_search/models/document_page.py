# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import models
from odoo.osv import expression

POSITIVE_TEXT_OPERATORS = ("like", "ilike", "=like", "=ilike")


class DocumentPage(models.Model):
    _inherit = "document.page"

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
        page_ids = list({a.res_id for a in attachments if a.res_id})
        if not page_ids:
            return domain
        return expression.OR([domain, [("id", "in", page_ids)]])

    def reindex_attachment_content(self, batch_size=500, only_missing=True):
        """Recompute ``ir.attachment.index_content`` for the files attached to
        document pages, e.g. after a bulk migration that imported them without
        indexing. Reuses Odoo's ``ir.attachment._index`` and never writes the
        page ``content``, so no page revision is created.

        Called on a recordset it processes those pages' attachments; called on
        the model it processes every ``document.page`` attachment. ``batch_size``
        caps how many attachments are reindexed per call (re-run until
        ``processed`` is 0); ``only_missing`` skips attachments that already have
        indexed content.

        Returns ``{"processed", "skipped", "no_text"}``: ``processed`` how many
        were reindexed, ``skipped`` how many were left untouched (already indexed
        or without data), and ``no_text`` the ``(id, name)`` of attachments that
        yielded no extractable text (scanned PDFs, or PDFs indexed without
        ``pdfminer.six``).
        """
        attachment_model = self.env["ir.attachment"]
        domain = [("res_model", "=", "document.page")]
        if self:
            domain.append(("res_id", "in", self.ids))
        attachments = attachment_model.search(domain)
        processed = 0
        skipped = 0
        no_text = []
        for attachment in attachments:
            if batch_size and processed >= batch_size:
                break
            if only_missing and attachment.index_content:
                skipped += 1
                continue
            datas = attachment.with_context(bin_size=False).datas
            if not datas:
                skipped += 1
                continue
            content = attachment._index(base64.b64decode(datas), attachment.mimetype)
            attachment.index_content = content
            processed += 1
            family = (attachment.mimetype or "").split("/")[0]
            if not content or content == family:
                no_text.append((attachment.id, attachment.name))
        return {"processed": processed, "skipped": skipped, "no_text": no_text}

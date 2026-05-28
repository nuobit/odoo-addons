# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from lxml import etree, html

from odoo import models

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
        attachments = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "document.page"),
                    ("index_content", operator, value),
                ]
            )
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
        return ["|"] + domain + [("id", "in", list(page_ids))]

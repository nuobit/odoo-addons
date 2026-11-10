# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from lxml import etree, html

from odoo import api, models

FILE_URL_RE = re.compile(r"/web/(?:content|image)/(\d+)")


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def _linked_file_ids(self, content):
        """Ids of the files that the links of the HTML ``content`` point to."""
        if not content:
            return set()
        try:
            tree = html.fragment_fromstring(content, create_parent=True)
        except (etree.ParserError, ValueError):
            return set()
        linked_ids = set()
        for url in tree.xpath(".//@href | .//@src"):
            match = FILE_URL_RE.search(url)
            if match:
                linked_ids.add(int(match.group(1)))
        return linked_ids

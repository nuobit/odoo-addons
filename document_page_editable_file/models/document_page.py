# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from lxml import etree, html

from odoo import api, fields, models
from odoo.tools import is_html_empty

FILE_URL_RE = re.compile(r"/web/(?:content|image)/(\d+)")


class DocumentPage(models.Model):
    _inherit = "document.page"

    editable_content = fields.Html(
        string="Editables",
        groups="document_page.group_document_editor",
    )

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

    def _keep_editable_files(self, editable_content, uploaded_on):
        """Make files of the editable content of this page the files that
        ``editable_content``, the editable content saved on ``uploaded_on`` (this
        page or one of its versions), links and that the current user uploaded
        there (any upload, for a system administrator). They stop being attachments
        of the record, so neither its chatter nor the searches show them, and only
        whoever can read the editable content of the page gets them.
        """
        self.ensure_one()
        files = (
            self.env["ir.attachment"]
            .sudo()
            .browse(sorted(self._linked_file_ids(editable_content)))
            .exists()
            .filtered(
                lambda a: a.res_model == uploaded_on._name
                and (not a.res_id or a.res_id == uploaded_on.id)
                and not a.res_field
                and (self.env.is_system() or a.create_uid == self.env.user)
            )
        )
        if files:
            files.with_env(self.env).write(
                {
                    "res_model": self._name,
                    "res_id": self.id,
                    "res_field": "editable_content",
                }
            )

    def _create_history(self, vals):
        # The version that a save creates takes the editable content of the
        # document, as it takes its content. Whoever can change the content can
        # read this field: both are for the Knowledge editors
        editable_content = self.editable_content
        if not is_html_empty(editable_content):
            vals = dict(vals, editable_content=editable_content)
        return super()._create_history(vals)

    @api.model_create_multi
    def create(self, vals_list):
        pages = super().create(vals_list)
        for page, vals in zip(pages, vals_list):
            if "editable_content" in vals:
                page._keep_editable_files(vals["editable_content"], page)
        return pages

    def write(self, vals):
        if "editable_content" not in vals:
            return super().write(vals)
        versions = self.env["document.page.history"]
        old_versions = versions.search([("page_id", "in", self.ids)])
        res = super().write(vals)
        new_versions = versions.search([("page_id", "in", self.ids)]) - old_versions
        # A save that creates no version puts the editable content in the current
        # one, as the name and the summary of the revision do
        for page in self - new_versions.page_id:
            if not is_html_empty(page.editable_content):
                page.history_head.editable_content = page.editable_content
        for page in self:
            page._keep_editable_files(vals["editable_content"], page)
        return res

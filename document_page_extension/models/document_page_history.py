# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from lxml import etree, html

from odoo import api, models

FILE_URL_RE = re.compile(r"/web/(?:content|image)/(\d+)")


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    # A file inserted in the content of a version not saved yet belongs to no
    # record, since the version has no id yet, and only its uploader and the
    # system administrators get a file of no record. Saving the version makes it
    # a file of the version, as those inserted once it exists, so whoever can
    # read its page gets it

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

    def _keep_uploaded_files(self, content):
        """Make files of this version the files that ``content``, the content being
        saved, links and that the current user uploaded on a version not saved yet
        (any such upload, for a system administrator).
        """
        self.ensure_one()
        files = (
            self.env["ir.attachment"]
            .sudo()
            .browse(sorted(self._linked_file_ids(content)))
            .exists()
            .filtered(
                lambda a: a.res_model == self._name
                and not a.res_id
                and not a.res_field
                and (self.env.is_system() or a.create_uid == self.env.user)
            )
        )
        if files:
            files.with_env(self.env).write({"res_model": self._name, "res_id": self.id})

    @api.model_create_multi
    def create(self, vals_list):
        versions = super().create(vals_list)
        for version, vals in zip(versions, vals_list):
            if "content" in vals:
                version._keep_uploaded_files(vals["content"])
        return versions

    def write(self, vals):
        res = super().write(vals)
        if "content" in vals:
            for version in self:
                version._keep_uploaded_files(vals["content"])
        return res

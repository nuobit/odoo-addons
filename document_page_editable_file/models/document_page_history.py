# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    editable_content = fields.Html(
        string="Editables",
        groups="document_page.group_document_editor",
    )

    # The files uploaded on the editable content of a version become files of the
    # editable content of its page, as those uploaded on the page do. A version
    # without a page keeps them as its attachments

    @api.model_create_multi
    def create(self, vals_list):
        versions = super().create(vals_list)
        for version, vals in zip(versions, vals_list):
            if "editable_content" in vals and version.page_id:
                version.page_id._keep_editable_files(vals["editable_content"], version)
        return versions

    def write(self, vals):
        res = super().write(vals)
        if "editable_content" in vals:
            for version in self.filtered("page_id"):
                version.page_id._keep_editable_files(vals["editable_content"], version)
        return res

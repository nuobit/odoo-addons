# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    editable_content = fields.Html(
        string="Editables",
        groups="document_page_editable_file.group_document_editable_file,"
        "document_page.group_document_manager",
    )

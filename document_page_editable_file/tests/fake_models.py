# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentPageEditableFile(models.Model):
    """A field that another module adds to the editable files."""

    _inherit = "document.page.editable.file"

    revision = fields.Char()

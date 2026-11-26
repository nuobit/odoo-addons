# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.depends("is_approval_required")
    def _compute_editables_locked(self):
        # A document that requires approval shows no version until its first change
        # request is approved: until then its files change in that change request
        super()._compute_editables_locked()
        for page in self:
            if page.is_approval_required and not page.history_head:
                page.editables_locked = True

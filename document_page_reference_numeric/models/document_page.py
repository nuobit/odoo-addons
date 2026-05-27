# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if not vals.get("reference"):
                reference = sequence.next_by_code("document.page.reference.numeric")
                while reference and self.with_context(active_test=False).search_count(
                    [("reference", "=", reference)]
                ):
                    reference = sequence.next_by_code("document.page.reference.numeric")
                vals["reference"] = reference
        return super().create(vals_list)

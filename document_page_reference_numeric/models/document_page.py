# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError

SEQUENCE_CODE = "document.page.reference.numeric"


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        # Any document holding the number counts, seen by the user or not
        pages = self.sudo().with_context(active_test=False)
        for vals in vals_list:
            if not vals.get("reference"):
                reference = sequence.next_by_code(SEQUENCE_CODE)
                while reference and pages.search_count([("reference", "=", reference)]):
                    reference = sequence.next_by_code(SEQUENCE_CODE)
                if not reference:
                    raise UserError(
                        _(
                            "There is no active sequence with code %s to generate a "
                            "numeric reference. Type a reference, or ask an "
                            "administrator to restore the sequence.",
                            SEQUENCE_CODE,
                        )
                    )
                vals["reference"] = reference
        return super().create(vals_list)

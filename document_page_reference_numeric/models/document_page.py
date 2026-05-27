# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

INT4_MAX = 2147483647


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.constrains("reference")
    def _check_reference_fits_int4(self):
        for page in self:
            reference = page.reference or ""
            if reference.isdigit() and int(reference) >= INT4_MAX:
                raise ValidationError(
                    _(
                        "Numeric reference %(ref)s is too large: it must be below %(max)s."
                    )
                    % {"ref": reference, "max": INT4_MAX}
                )

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

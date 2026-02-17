# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models, tools
from odoo.exceptions import ValidationError


class UoM(models.Model):
    _inherit = "uom.uom"

    @api.constrains("rounding", "factor", "uom_type", "category_id")
    def _check_rounding_factor_coherence(self):
        """Ensure UoM rounding is fine enough relative to the conversion ratio.

        When converting quantities between UoMs in the same category,
        a non-reference UoM whose rounding is too coarse relative to
        its conversion factor will lose precision beyond the reference
        UoM's rounding. For example, if the reference UoM has rounding
        0.001 and a secondary UoM with ratio 1.141 has rounding 0.01,
        each conversion can introduce up to ±0.004 error in reference
        units — enough to accumulate visible discrepancies over
        multiple transactions.

        The check: converting the UoM's rounding step to reference units
        (rounding / factor) must not exceed the reference UoM's rounding.
        """
        categories = self.mapped("category_id")
        for category in categories:
            uoms = self.env["uom.uom"].search(
                [
                    ("category_id", "=", category.id),
                    ("active", "=", True),
                ]
            )
            ref_uom = uoms.filtered(lambda u: u.uom_type == "reference")
            if len(ref_uom) != 1:
                raise ValidationError(
                    _(
                        "Cannot validate rounding coherence for "
                        "category '%(category)s': expected exactly one "
                        "active reference unit of measure but found "
                        "%(count)s."
                    )
                    % {
                        "category": category.name,
                        "count": len(ref_uom),
                    }
                )
            for uom in uoms - ref_uom:
                # Convert this UoM's rounding to reference units
                # Using the same formula as _compute_quantity:
                #   amount = qty / self.factor * to_unit.factor
                # Since ref_uom.factor = 1.0:
                #   rounding_in_ref = uom.rounding / uom.factor
                rounding_in_ref = uom.rounding / uom.factor
                if (
                    tools.float_compare(
                        rounding_in_ref,
                        ref_uom.rounding,
                        precision_rounding=ref_uom.rounding,
                    )
                    > 0
                ):
                    raise ValidationError(
                        _(
                            "The rounding precision of '%(uom)s' (%(uom_rounding)s) "
                            "is too coarse for its conversion ratio (%(factor)s). "
                            "When converted to the reference unit '%(ref)s', "
                            "the effective rounding becomes %(effective)s, "
                            "which exceeds the reference rounding of "
                            "%(ref_rounding)s.\n\n"
                            "To fix this, either decrease the rounding of "
                            "'%(uom)s' or increase the rounding of '%(ref)s'."
                        )
                        % {
                            "uom": uom.name,
                            "uom_rounding": uom.rounding,
                            "factor": uom.factor,
                            "ref": ref_uom.name,
                            "effective": rounding_in_ref,
                            "ref_rounding": ref_uom.rounding,
                        }
                    )

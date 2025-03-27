# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    is_opt_in = fields.Boolean(
        copy=False,
        tracking=True,
        help="Indicates if this activity requires user consent to "
        "receive communications.",
    )

    @api.constrains
    def _check_is_opt_in(self):
        for rec in self:
            if rec.is_opt_in:
                if self.env["privacy.activity"].search_count(
                    [("is_opt_in", "=", True), ("id", "!=", rec.id)]
                ):
                    raise ValidationError(_("There can be only one opt-in activity."))
                if not rec.consent_required:
                    raise ValidationError(_("Opt-in activity must require consent."))

    def action_is_opt_in(self):
        self.ensure_one()
        self.is_opt_in = not self.is_opt_in

# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import html2plaintext


class PrivacyActivity(models.Model):
    _inherit = "privacy.activity"

    privacy_policy = fields.Boolean(copy=False, tracking=True)

    @api.constrains
    def _check_privacy_policy(self):
        for rec in self:
            if rec.privacy_policy:
                if self.env["privacy.activity"].search_count(
                    [("privacy_policy", "=", True), ("id", "!=", rec.id)]
                ):
                    raise ValidationError(
                        _("There can be only one privacy policy activity.")
                    )
            if not rec.consent_required:
                raise ValidationError(
                    _("Privacy Policy activity must require consent.")
                )

    def action_privacy_policy(self):
        self.ensure_one()
        self.privacy_policy = not self.privacy_policy

    def description_has_text(self):
        if not self.description:
            return False
        plain_text = html2plaintext(self.description).strip()
        alphanumeric_text = re.sub(r"[^\w]+", "", plain_text)
        return bool(alphanumeric_text)

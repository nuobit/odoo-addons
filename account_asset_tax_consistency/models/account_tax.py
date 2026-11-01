# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    apply_to_asset = fields.Selection(
        [
            ("ignore", "Ignore"),
            ("always", "Always"),
            ("never", "Never"),
        ],
        string="Apply to asset",
        required=True,
        default="ignore",
    )

    def check_asset_profile(self, profile):
        if profile:
            apply_to_asset = {}
            for rec in self:
                apply_to_asset.setdefault(rec.apply_to_asset, self.env[self._name])
                apply_to_asset[rec.apply_to_asset] |= rec
            error_message = _(
                "Defined taxes %s are not applicable with assets. "
                "Please enter the taxes accordingly."
            )
            if "never" in apply_to_asset:
                raise ValidationError(
                    error_message % apply_to_asset["never"].mapped("name")
                )
            if "always" not in apply_to_asset:
                raise ValidationError(error_message % self.mapped("name"))

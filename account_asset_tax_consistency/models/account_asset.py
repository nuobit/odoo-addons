# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    @api.constrains("profile_id", "tax_ids")
    def _check_taxes_asset_profile(self):
        for rec in self:
            if rec.tax_ids:
                rec.tax_ids.check_asset_profile(rec.profile_id)

    def unlink(self):
        # Necessary due to flush on Odoo core (account.acount_move._check_balanced)
        return super(
            AccountAsset, self.with_context(allow_remove_asset_no_check=True)
        ).unlink()

# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains("asset_profile_id", "tax_ids")
    def _check_taxes_move_line_profile(self):
        for rec in self:
            if rec.tax_ids:
                if not self.env.context.get("allow_remove_asset_no_check"):
                    rec.tax_ids.check_asset_profile(rec.asset_profile_id)

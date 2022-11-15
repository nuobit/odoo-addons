# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains("asset_profile_id", "tax_ids")
    def _check_move_line_taxes_asset_profile(self):
        for rec in self:
            self.env['account.tax'].check_duplicated_vat_taxes(rec.tax_ids)

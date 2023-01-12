# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        threshold_amount = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_es_account_capital_asset.capital_asset_threshold_amount")
        )
        if aml.balance >= threshold_amount:
            vals["capital_asset_type_id"] = aml.asset_profile_id.capital_asset_type_id
        return vals

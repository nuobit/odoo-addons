# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        if aml.company_id.l10n_es_capital_asset_enabled:
            threshold_amount = float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "l10n_es_account_capital_asset.capital_asset_threshold_amount"
                )
            )
            if aml.balance >= threshold_amount:
                capital_asset_type = aml.asset_profile_id.default_capital_asset_type_id
                if not capital_asset_type:
                    raise UserError(
                        _(
                            "The asset profile '%(profile)s' requires a default "
                            "capital asset type because the invoice line amount "
                            "is equal to or greater than %(amount)s. Please "
                            "configure the asset profile before posting the "
                            "invoice.",
                            profile=aml.asset_profile_id.display_name,
                            amount=threshold_amount,
                        )
                    )
                vals["capital_asset_type_id"] = capital_asset_type.id
        return vals

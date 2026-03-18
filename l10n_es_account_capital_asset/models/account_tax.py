# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    def check_tax_base_amount(self, asset):
        threshold_amount = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_es_account_capital_asset.capital_asset_threshold_amount")
        )
        tax_mappings = self.env["l10n.es.account.capital.asset.map.tax"].search([])
        capital_asset_dest_taxes = tax_mappings.mapped("tax_dest_id")

        for rec in self:
            if rec.company_id.l10n_es_capital_asset_enabled:
                is_capital_asset_tax = rec in capital_asset_dest_taxes
                if (
                    not asset.profile_id.asset_product_item
                    and asset.profile_id.capital_asset_set
                ):
                    tax_base_amount_unit = asset.tax_base_amount_unit
                else:
                    tax_base_amount_unit = asset.tax_base_amount
                if (
                    tax_base_amount_unit >= threshold_amount
                    and not is_capital_asset_tax
                ):
                    raise ValidationError(
                        _(
                            "The asset of type '%(asset_type)s' has a unit amount "
                            "%(unit_amount).2f€ greater than %(threshold).2f€, so "
                            "it is considered a capital asset, but the selected "
                            "taxes are not of a capital asset type. Please update "
                            "the taxes accordingly or define the asset type as"
                            " a set of assets."
                        )
                        % {
                            "asset_type": asset.profile_id.name,
                            "unit_amount": tax_base_amount_unit,
                            "threshold": threshold_amount,
                        }
                    )
                elif tax_base_amount_unit < threshold_amount and is_capital_asset_tax:
                    raise ValidationError(
                        _(
                            "The asset of type '%(asset_type)s' has a unit amount"
                            " %(unit_amount).2f€ lower than %(threshold).2f€, so "
                            "it is not considered a capital asset, but capital "
                            "asset taxes are selected. Please update the taxes "
                            "accordingly or define the asset type as a set of "
                            "assets."
                        )
                        % {
                            "asset_type": asset.profile_id.name,
                            "unit_amount": tax_base_amount_unit,
                            "threshold": threshold_amount,
                        }
                    )

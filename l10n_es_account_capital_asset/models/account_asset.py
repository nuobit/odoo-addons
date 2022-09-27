# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.account_asset_management.models.account_asset import READONLY_STATES


class AccountAsset(models.Model):
    _inherit = "account.asset"

    profile_capital_asset_type_id = fields.Many2one(
        string="Capital Asset Profile Type",
        related="profile_id.capital_asset_type_id",
    )
    capital_asset_type_id = fields.Many2one(
        comodel_name="l10n.es.account.capital.asset.type",
        ondelete="restrict",
        states=READONLY_STATES,
        domain="[('id', '=', profile_capital_asset_type_id)]",
    )

    @api.constrains("tax_base_amount_unit", "capital_asset_type_id", "company_id")
    def _check_amount_type(self):
        threshold_capital_asset_amount = float(
            self.env["ir.config_parameter"].get_param(
                "l10n_es_account_capital_asset.capital_asset_threshold_amount"
            )
        )
        for rec in self:
            if rec.company_id.l10n_es_capital_asset_enabled:
                if (
                    rec.tax_base_amount_unit >= threshold_capital_asset_amount
                    and not rec.capital_asset_type_id
                ):
                    raise ValidationError(
                        _(
                            "If Tax Base Amount is greater than %s, "
                            "capital asset type must be defined."
                        )
                        % threshold_capital_asset_amount
                    )
                if (
                    rec.tax_base_amount_unit < threshold_capital_asset_amount
                    and rec.capital_asset_type_id
                ):
                    raise ValidationError(
                        _(
                            "If Tax Base Amount is less than %s, this asset "
                            "is not considered as a "
                            "capital asset so capital asset type mustn't be defined"
                        )
                        % threshold_capital_asset_amount
                    )

    @api.constrains("tax_base_amount_unit", "tax_ids")
    def _check_tax_base_amount(self):
        if not self.mapped("tax_ids") and self.env.context.get(
            "allow_empty_taxes", False
        ):
            return
        for rec in self:
            self.tax_ids.check_tax_base_amount(rec.tax_base_amount_unit)

    @api.constrains("profile_id", "capital_asset_type_id")
    def _check_capital_asset_type_integrity(self):
        if (
            self.capital_asset_type_id
            and self.profile_id.capital_asset_type_id != self.capital_asset_type_id
        ):
            raise ValidationError(
                _(
                    "Capital asset type must be the same as "
                    "the one defined in the asset category."
                )
            )

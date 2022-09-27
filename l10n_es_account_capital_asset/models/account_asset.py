# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    capital_asset_type_id = fields.Many2one(
        comodel_name="l10n.es.account.capital.asset.type",
        ondelete="restrict",
    )

    @api.constrains("tax_base_amount", "capital_asset_type_id")
    def _check_amount_type(self):
        threshold_capital_asset_amount = float(
            self.env["ir.config_parameter"].get_param(
                "account_capital_asset.capital_asset_threshold_amount"
            )
        )
        for rec in self:
            if (
                rec.tax_base_amount >= threshold_capital_asset_amount
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
                rec.tax_base_amount < threshold_capital_asset_amount
                and rec.capital_asset_type_id
            ):
                raise ValidationError(
                    _(
                        "If Tax Base Amount is less than %s, this asset is not considered as a "
                        "capital asset so capital asset type mustn't be defined"
                    )
                    % threshold_capital_asset_amount
                )

    @api.constrains("tax_base_amount", "tax_ids")
    def _check_tax_base_amount(self):
        if not self.tax_ids and self.env.context.get("allow_empty_taxes", False):
            return
        threshold_amount = float(
            self.env["ir.config_parameter"].get_param(
                "account_capital_asset.capital_asset_threshold_amount"
            )
        )
        bi_tax_templates = self.env["l10n.es.account.capital.asset.map.tax"].search([])
        bi_dest_taxes = self.company_id.get_taxes_from_templates(
            bi_tax_templates.tax_dest_id
        )
        taxes = self.tax_ids.filtered(lambda x: x in bi_dest_taxes)
        if self.tax_base_amount >= threshold_amount and not taxes:
            raise ValidationError(
                _(
                    "Capital Asset don't have Capital Asset tax."
                    " Please, review the taxes"
                )
                % self.display_name
            )
        if self.tax_base_amount < threshold_amount and taxes:
            raise ValidationError(
                _("Asset have Capital Asset tax." " Please, review the taxes")
                % self.display_name
            )

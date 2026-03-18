# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountCapitalAssetMapTax(models.Model):
    _name = "l10n.es.account.capital.asset.map.tax"
    _description = "Capital Asset Map Tax"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    tax_src_id = fields.Many2one(
        comodel_name="account.tax",
        string="Tax Source",
        required=True,
        check_company=True,
    )
    tax_dest_id = fields.Many2one(
        comodel_name="account.tax",
        string="Replacement Tax",
        required=True,
        check_company=True,
    )

    def _get_taxes_mapping(self):
        return {mapping.tax_src_id: mapping.tax_dest_id for mapping in self.search([])}

    @api.model
    def map_tax(self, taxes, company, asset_profile, amount, quantity):
        if any(
            [
                not taxes,
                not company,
                not company.l10n_es_capital_asset_enabled,
                not asset_profile,
                not amount,
                not quantity,
            ]
        ):
            return taxes
        threshold_capital_asset_amount = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_es_account_capital_asset.capital_asset_threshold_amount")
        )
        asset_price = amount
        result = taxes
        if asset_price >= float(threshold_capital_asset_amount):
            tax_map = self._get_taxes_mapping()
            result = self.env["account.tax"]
            for tax in taxes:
                result |= tax_map.get(tax._origin, tax)
        return result

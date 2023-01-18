# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountCapitalAssetMapTax(models.Model):
    _name = "l10n.es.account.capital.asset.map.tax"
    _description = "Capital Asset Map Tax"

    tax_src_id = fields.Many2one(
        "account.tax.template", string="Tax Source", required=True
    )
    tax_dest_id = fields.Many2one(
        "account.tax.template", string="Replacement Tax", required=True
    )

    # TODO: Refactor to do this function more efficient or do it with ormcache
    # @ormcache("tax_template", "company","tax_src_id","tax_dest_id")
    def _get_taxes_mapping_from_tax_templates(self, company):
        return {
            company.get_taxes_from_templates(
                x.tax_src_id
            ): company.get_taxes_from_templates(x.tax_dest_id)
            for x in self.search([])
        }

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
        asset_price = self.env["account.asset"]._get_asset_unit_price(amount, quantity)
        result = taxes
        if asset_price >= float(threshold_capital_asset_amount):
            tax_map = self._get_taxes_mapping_from_tax_templates(company)
            result = self.env["account.tax"]
            for tax in taxes:
                result |= tax_map[tax._origin] if tax._origin in tax_map else tax
        return result

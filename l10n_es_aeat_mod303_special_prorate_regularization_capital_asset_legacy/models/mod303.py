# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    def _prepare_tax_line_vals_dates(self, date_start, date_end, map_line):
        tax_line_vals = super()._prepare_tax_line_vals_dates(
            date_start, date_end, map_line
        )
        asset_ids = self.env["account.asset"].search(
            [
                ("invoice_move_line_id", "=", False),
                ("prorate_tax_id", "in", self.get_taxes_from_map(map_line).ids),
            ]
        )
        tax_line_vals["asset_ids"] = [(6, 0, asset_ids.ids)]
        return tax_line_vals

    def _get_assets_from_tax_line_vals(self, tax_line_vals):
        assets = super()._get_assets_from_tax_line_vals(tax_line_vals)
        return assets | self.env["account.asset"].browse(
            tax_line_vals["asset_ids"][0][2]
        )

    def _prepare_move_lines(self, tax_lines):
        move_lines_values = super()._prepare_move_lines(tax_lines)
        for asset in tax_lines.asset_ids:
            deductible_line = self._calculate_repartition_tax(asset)
            move_lines_values.append(
                {
                    "asset_id": [asset.id, asset.name],
                    "name": deductible_line.account_id.name,
                    "account_id": [
                        deductible_line.account_id,
                        deductible_line.account_id.name,
                    ],
                    "debit": asset.purchase_value if asset.purchase_value >= 0 else 0,
                    "credit": -asset.purchase_value if asset.purchase_value < 0 else 0,
                }
            )
        return move_lines_values

    def _calculate_repartition_tax(self, asset):
        if asset.invoice_move_line_id:
            deductible_line = super()._calculate_repartition_tax(asset)
        else:
            repartition_lines = (
                asset.prorate_tax_id.invoice_repartition_line_ids
                if asset.purchase_value >= 0
                else asset.prorate_tax_id.refund_repartition_line_ids
            )
            deductible_line = self._extract_deductible_repartition_line(
                repartition_lines
            )
        return deductible_line

    def _updated_tax_line_vals_capital_asset(self, assets, tax_final_percentage):
        return {
            **super()._updated_tax_line_vals_capital_asset(
                assets, tax_final_percentage
            ),
            "asset_ids": [
                (6, 0, assets.filtered(lambda x: not x.invoice_move_line_id).ids)
            ],
        }

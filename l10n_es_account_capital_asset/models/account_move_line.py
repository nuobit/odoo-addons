# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange(
        "product_id",
        "product_uom_id",
        "account_id",
        "tax_ids",
        "asset_profile_id",
        "price_subtotal",
        "quantity",
    )
    def _onchange_recompute_mapped_taxes(self):
        self.compute_mapped_taxes()

    def _compute_tax_ids(self):
        res = super()._compute_tax_ids()
        self.compute_mapped_taxes()
        return res

    def _inverse_account_id(self):
        res = super()._inverse_account_id()
        self.compute_mapped_taxes()
        return res

    def compute_mapped_taxes(self):
        for line in self:
            if line.tax_ids:
                line.tax_ids = line.env[
                    "l10n.es.account.capital.asset.map.tax"
                ].map_tax(
                    line.tax_ids,
                    line.company_id,
                    line.asset_profile_id,
                    line.balance,
                    line.quantity,
                )
        return self

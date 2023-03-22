# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        self.compute_mapped_taxes()

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        super()._onchange_uom_id()
        self.compute_mapped_taxes()

    @api.onchange("account_id")
    def _onchange_account_id(self):
        super()._onchange_uom_id()
        self.compute_mapped_taxes()

    @api.onchange("tax_ids")
    def _onchange_tax_ids(self):
        self.compute_mapped_taxes()

    @api.onchange("asset_profile_id")
    def _onchange_asset_profile_id(self):
        super()._onchange_asset_profile_id()
        self.compute_mapped_taxes()

    @api.onchange("price_subtotal", "quantity")
    def _onchange_subtotal_quantity_id(self):
        self.compute_mapped_taxes()

    def compute_mapped_taxes(self):
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids,
                self.company_id,
                self.asset_profile_id,
                self.balance,
                self.quantity,
            )

# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.balance, self.quantity
            )

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        super()._onchange_uom_id()
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.balance, self.quantity
            )

    @api.onchange("account_id")
    def _onchange_account_id(self):
        super()._onchange_uom_id()
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.balance, self.quantity
            )

    @api.onchange("price_subtotal", "quantity")
    def _onchange_subtotal_quantity_id(self):
        taxes = self._get_computed_taxes()
        if taxes and self.move_id.fiscal_position_id:
            taxes = self.move_id.fiscal_position_id.map_tax(
                taxes, partner=self.partner_id
            )
        if taxes:
            taxes = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                taxes, self.company_id, self.balance, self.quantity
            )
        self.tax_ids = taxes

    @api.onchange("tax_ids")
    def _onchange_tax_ids(self):
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.balance, self.quantity
            )

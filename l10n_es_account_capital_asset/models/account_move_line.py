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
                self.tax_ids, self.company_id, self.price_subtotal, self.quantity
            )

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        super()._onchange_uom_id()
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.price_subtotal, self.quantity
            )

    @api.onchange("account_id")
    def _onchange_account_id(self):
        super()._onchange_uom_id()
        if self.tax_ids:
            self.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                self.tax_ids, self.company_id, self.price_subtotal, self.quantity
            )

    @api.onchange("price_subtotal", "quantity")
    def _onchange_subtotal_quantity_id(self):
        for line in self:
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(
                    taxes, partner=line.partner_id
                )
            if taxes:
                taxes = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                    taxes, line.company_id, line.price_subtotal, line.quantity
                )
            line.tax_ids = taxes

    @api.onchange("tax_ids")
    def _onchange_tax_ids(self):
        for rec in self:
            if rec.tax_ids:
                rec.tax_ids = self.env["l10n.es.account.capital.asset.map.tax"].map_tax(
                    rec.tax_ids, rec.company_id, rec.price_subtotal, rec.quantity
                )

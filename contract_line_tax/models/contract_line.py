# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
        context={"active_test": False},
        check_company=True,
    )

    def _prepare_invoice_line(self):
        self.ensure_one()
        res = super()._prepare_invoice_line()

        taxes = self.tax_ids or self.product_id.taxes_id
        if taxes:
            fiscal_position = self.contract_id.fiscal_position_id or self.env[
                "account.fiscal.position"
            ]._get_fiscal_position(self.contract_id.partner_id)
            if fiscal_position:
                taxes = fiscal_position.map_tax(
                    taxes, partner=self.contract_id.partner_id
                )
        res.update(
            {
                "tax_ids": [(6, 0, taxes.ids)] if taxes else [],
            }
        )
        return res

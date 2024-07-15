# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
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

    def _prepare_invoice_line(self, move_form):
        self.ensure_one()
        res = super(ContractLine, self)._prepare_invoice_line(move_form)
        taxes = self.tax_ids or self.product_id.taxes_id
        if taxes:
            fiscal_position = self.contract_id.fiscal_position_id or self.env[
                "account.fiscal.position"
            ].get_fiscal_position(self.partner_id.id)
            if fiscal_position:
                taxes = fiscal_position.map_tax(taxes, partner=self.partner_id)
        res.update(
            {
                "tax_ids": taxes.ids and [(6, 0, taxes.ids)] or [],
            }
        )
        return res

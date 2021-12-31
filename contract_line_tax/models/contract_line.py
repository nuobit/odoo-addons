# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
    )

    def _prepare_invoice_line(self, move_form):
        self.ensure_one()
        res = super(ContractLine, self)._prepare_invoice_line(move_form)
        res.update(
            {
                "tax_ids": self.tax_ids.ids and [(6, 0, self.tax_ids.ids)] or [],
            }
        )
        return res

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    comment = fields.Text("Additional Information")

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(date_invoice, journal)
        invoice_vals.update({"narration": self.comment})
        return invoice_vals, move_form

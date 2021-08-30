# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    date_invoice = fields.Date(string="Invoice date")

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )
        invoice.write({"date_invoice": self.date_invoice})
        return invoice

    @api.multi
    def create_invoices(self):
        if self.date_invoice:
            self = self.with_context(date_invoice=self.date_invoice)

        return super(SaleAdvancePaymentInv, self).create_invoices()

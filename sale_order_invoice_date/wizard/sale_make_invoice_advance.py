# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date(string="Invoice date")

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )
        invoice.write({"invoice_date": self.invoice_date})
        return invoice

    def create_invoices(self):
        if self.invoice_date:
            self = self.with_context(invoice_date=self.invoice_date)
        return super(SaleAdvancePaymentInv, self).create_invoices()

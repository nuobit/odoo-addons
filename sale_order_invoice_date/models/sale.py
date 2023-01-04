# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super(SaleOrder, self)._create_invoices(
            grouped=grouped, final=final, date=date
        )
        if invoices:
            invoice_date = self.env.context.get("invoice_date")
            if invoice_date:
                invoices.write(
                    {
                        "invoice_date": invoice_date,
                        "date": invoice_date,
                    }
                )

        return invoices

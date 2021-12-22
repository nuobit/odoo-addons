# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super(SaleOrder, self)._create_invoices(
            grouped=grouped, final=final, date=date
        )
        if moves:
            batch_id = self.env.context.get("batch_id")
            if batch_id:
                for move in moves:
                    values = {
                        "invoice_batch_id": batch_id,
                    }
                    if move.partner_id.invoice_batch_sending_method:
                        values[
                            "invoice_batch_sending_method"
                        ] = move.partner_id.invoice_batch_sending_method
                    if move.partner_id.invoice_batch_email_partner_id:
                        values[
                            "invoice_batch_email_partner_id"
                        ] = move.partner_id.invoice_batch_email_partner_id.id
                    move.write(values)
        return moves

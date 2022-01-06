# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, final=final
        )
        for invoice in self.env["account.invoice"].browse(invoice_ids):
            if invoice.facturae:
                for line in invoice.invoice_line_ids:
                    order = line.sale_line_ids.mapped("order_id")
                    if order:
                        if len(order) > 1:
                            raise UserError(
                                _(
                                    "The invoice line with id '%i' references more than one order"
                                )
                                % invoice.id
                            )
                        values = {}
                        if order.insured_ident_cardnum:
                            values[
                                "facturae_file_reference"
                            ] = order.insured_ident_cardnum
                        if order.policy_number:
                            values[
                                "facturae_receiver_transaction_reference"
                            ] = order.policy_number
                        if order.auth_number:
                            values[
                                "facturae_receiver_contract_reference"
                            ] = order.auth_number
                        if order.service_date:
                            values[
                                "facturae_receiver_transaction_date"
                            ] = order.service_date
                        if values:
                            line.write(values)
        return invoice_ids

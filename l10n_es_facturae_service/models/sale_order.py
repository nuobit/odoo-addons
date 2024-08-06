# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        order = self.order_id
        return super()._prepare_invoice_line(
            facturae_file_reference=order.insured_ident_cardnum,
            facturae_receiver_transaction_reference=order.policy_number,
            facturae_receiver_contract_reference=order.auth_number,
            facturae_receiver_transaction_date=fields.Date.context_today(
                order.with_context(tz=self.create_uid.tz), order.service_date
            ),
        )

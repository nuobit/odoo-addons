# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class OXigestiSPMSAccountInvoiceListener(Component):
    _name = "oxigesti.spms.account.invoice.listener"
    _inherit = "base.event.listener"

    _apply_on = "account.move"

    def on_validated_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.sale_line_ids.order_id:
            invoices = order.invoice_ids.filtered(
                lambda inv: inv != record and inv.state == "posted"
            )
            if invoices:
                raise UserError(
                    _(
                        "This invoice cannot be validated because the "
                        "associated sales order already has related invoice lines. "
                        "Please review the sales order and ensure it does "
                        "not have any existing invoices linked before proceeding."
                    )
                )
            binding = order.oxigesti_spms_bind_ids
            if binding:
                binding.ensure_one()
                binding.export_invoice_data(record)

    def on_cancel_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.mapped("sale_line_ids.order_id"):
            binding = order.oxigesti_spms_bind_ids
            if binding:
                binding.ensure_one()
                binding.export_invoice_data(record, clear=True)

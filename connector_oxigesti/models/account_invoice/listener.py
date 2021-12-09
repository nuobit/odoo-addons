# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OXigestiAccountInvoiceListener(Component):
    _name = "oxigesti.account.invoice.listener"
    _inherit = "base.event.listener"

    _apply_on = "account.invoice"

    def on_validate_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.mapped("sale_line_ids.order_id"):
            binding = order.oxigesti_bind_ids
            if binding:
                binding.ensure_one()
                # exportem el numero de factura i la data
                binding.export_invoice_data(record)

    def on_cancel_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.mapped("sale_line_ids.order_id"):
            binding = order.oxigesti_bind_ids
            if binding:
                binding.ensure_one()
                # esborrem el numero de factura i la data
                binding.export_invoice_data(record, clear=True)

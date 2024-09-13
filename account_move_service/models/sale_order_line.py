# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _get_invoice_qty(self):
        records = self
        invoice_line_qty_invoiced = {}
        for rec in self.sorted("id"):
            if rec.order_id.partner_id.service_intermediary:
                qty_invoiced = 0.0
                for invoice_line in rec.invoice_lines.sorted("id"):
                    qty = invoice_line_qty_invoiced.setdefault(invoice_line.id, 0.0)
                    actual_qty_to_invoice = invoice_line.quantity - qty
                    if actual_qty_to_invoice > 0:
                        if rec.product_uom_qty < actual_qty_to_invoice:
                            actual_qty = invoice_line.product_uom_id._compute_quantity(
                                rec.product_uom_qty, rec.product_uom
                            )
                        else:
                            actual_qty = invoice_line.product_uom_id._compute_quantity(
                                actual_qty_to_invoice, rec.product_uom
                            )
                    else:
                        actual_qty = 0.0
                    invoice_line_qty_invoiced[invoice_line.id] += actual_qty
                    if invoice_line.move_id.state != "cancel":
                        qty_invoiced += actual_qty
                    elif invoice_line.move_id.move_type == "out_refund":
                        qty_invoiced -= actual_qty
                records -= rec
                rec.qty_invoiced = qty_invoiced
        return super(SaleOrderLine, records)._get_invoice_qty()

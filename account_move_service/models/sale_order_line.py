# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_subtotal_to_invoice = fields.Float(compute="_compute_price_to_invoice")
    price_total_to_invoice = fields.Float(compute="_compute_price_to_invoice")

    def _compute_price_to_invoice(self):
        for rec in self:
            res = self.env["account.move.line"]._get_price_total_and_subtotal_model(
                rec.price_unit,
                rec.qty_to_invoice,
                rec.discount,
                rec.currency_id,
                rec.product_id,
                rec.order_partner_id,
                rec.tax_id,
                False,
            )
            rec.price_subtotal_to_invoice = res.get("price_subtotal", 0.0)
            rec.price_total_to_invoice = res.get("price_total", 0.0)

    qty_to_invoice_service = fields.Float(compute="_compute_qty_to_invoice_service")

    def _compute_qty_to_invoice_service(self):
        for rec in self:
            if not rec.product_id or not rec.product_uom or not rec.product_uom_qty:
                rec.product_qty = 0.0
                continue
            product = self.env["account.move"].get_config_service_group_product(
                rec.order_id.company_id
            )
            rec.qty_to_invoice_service = rec.product_uom._compute_quantity(
                rec.qty_to_invoice, product.uom_id
            )

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _get_invoice_qty(self):
        records = self
        invoice_line_qty_invoiced = {}
        for rec in self.sorted("id"):
            if rec.order_id.partner_id.service_intermediary:
                qty_invoiced = 0.0
                qty_to_invoice = rec.product_uom_qty
                for invoice_line in rec.invoice_lines.sorted("id"):
                    qty = invoice_line_qty_invoiced.setdefault(invoice_line.id, 0.0)
                    actual_qty_to_invoice = (
                        invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity - qty - qty_invoiced, rec.product_uom
                        )
                    )
                    if actual_qty_to_invoice > 0:
                        if qty_to_invoice < actual_qty_to_invoice:
                            actual_qty = qty_to_invoice
                        else:
                            actual_qty = actual_qty_to_invoice
                    else:
                        actual_qty = 0.0
                    if invoice_line.move_id.state != "cancel":
                        invoice_line_qty_invoiced[
                            invoice_line.id
                        ] += rec.product_uom._compute_quantity(
                            actual_qty, invoice_line.product_uom_id
                        )
                        qty_to_invoice -= actual_qty
                        qty_invoiced += actual_qty
                    elif invoice_line.move_id.move_type == "out_refund":
                        invoice_line_qty_invoiced[
                            invoice_line.id
                        ] -= rec.product_uom._compute_quantity(
                            actual_qty, invoice_line.product_uom_id
                        )
                        qty_to_invoice += actual_qty
                        qty_invoiced -= actual_qty
                records -= rec
                rec.qty_invoiced = qty_invoiced
        return super(SaleOrderLine, records)._get_invoice_qty()

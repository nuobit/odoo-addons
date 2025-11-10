# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_subtotal_to_invoice = fields.Float(compute="_compute_price_to_invoice")
    price_total_to_invoice = fields.Float(compute="_compute_price_to_invoice")

    def _compute_price_to_invoice(self):
        AccountTax = self.env["account.tax"]
        for rec in self:
            base_line = AccountTax._prepare_base_line_for_taxes_computation(
                rec,
                price_unit=rec.price_unit,
                quantity=rec.qty_to_invoice,
                discount=rec.discount,
                currency_id=rec.currency_id,
                product_id=rec.product_id,
                tax_ids=rec.tax_id,
                partner_id=rec.order_partner_id,
            )
            AccountTax._add_tax_details_in_base_line(base_line, rec.company_id)
            rec.price_subtotal_to_invoice = base_line["tax_details"].get(
                "raw_total_excluded_currency", 0.0
            )
            rec.price_total_to_invoice = base_line["tax_details"].get(
                "raw_total_included_currency", 0.0
            )

    qty_to_invoice_service = fields.Float(compute="_compute_qty_to_invoice_service")

    def _compute_qty_to_invoice_service(self):
        for rec in self:
            if not rec.product_id or not rec.product_uom or not rec.product_uom_qty:
                rec.qty_to_invoice_service = 0.0
                continue
            product = self.env["account.move"].get_config_service_group_product(
                rec.order_id.company_id
            )
            rec.qty_to_invoice_service = rec.product_uom._compute_quantity(
                rec.qty_to_invoice, product.uom_id
            )

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _compute_qty_invoiced(self):
        service_lines = self.filtered(
            lambda lines: lines.order_id.partner_id.service_intermediary
        )
        other_lines = self - service_lines
        if other_lines:
            return super(SaleOrderLine, other_lines)._compute_qty_invoiced()

        invoice_line_qty_invoiced = {}
        for rec in service_lines.sorted("id"):
            qty_invoiced = 0.0
            qty_to_invoice = rec.product_uom_qty
            for invoice_line in rec._get_invoice_lines().sorted("id"):
                qty = invoice_line_qty_invoiced.setdefault(invoice_line.id, 0.0)
                actual_qty_to_invoice = invoice_line.product_uom_id._compute_quantity(
                    invoice_line.quantity - qty - qty_invoiced,
                    rec.product_uom,
                    round=False,
                )
                if actual_qty_to_invoice > 0:
                    if qty_to_invoice < actual_qty_to_invoice:
                        actual_qty = qty_to_invoice
                    else:
                        actual_qty = actual_qty_to_invoice
                else:
                    actual_qty = 0.0
                if (
                    invoice_line.move_id.state != "cancel"
                    or invoice_line.move_id.payment_state == "invoicing_legacy"
                ):
                    invoice_line_qty_invoiced[invoice_line.id] += (
                        rec.product_uom._compute_quantity(
                            actual_qty, invoice_line.product_uom_id, round=False
                        )
                    )
                    qty_to_invoice -= actual_qty
                    qty_invoiced += actual_qty
                elif invoice_line.move_id.move_type == "out_refund":
                    invoice_line_qty_invoiced[invoice_line.id] -= (
                        rec.product_uom._compute_quantity(
                            actual_qty, invoice_line.product_uom_id, round=False
                        )
                    )
                    qty_to_invoice += actual_qty
                    qty_invoiced -= actual_qty
            rec.qty_invoiced = qty_invoiced

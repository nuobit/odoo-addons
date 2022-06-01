# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_batch_create = fields.Boolean(string="Create invoice batch", default=True)
    in_background = fields.Boolean(string="In background", default=False)

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )
        if invoice:
            batch_id = self.env.context.get("batch_id")
            if batch_id:
                values = {
                    "invoice_batch_id": batch_id,
                }
                if invoice.partner_id.invoice_batch_sending_method:
                    values[
                        "invoice_batch_sending_method"
                    ] = invoice.partner_id.invoice_batch_sending_method
                if invoice.partner_id.invoice_batch_email_partner_id:
                    values[
                        "invoice_batch_email_partner_id"
                    ] = invoice.partner_id.invoice_batch_email_partner_id.id

                invoice.write(values)

        return invoice

    def create_invoice_group(self, order_group, invoice_batch=None):
        context = {"active_ids": order_group.mapped("id")}
        if invoice_batch:
            context.update(
                {
                    "batch_id": invoice_batch.id,
                }
            )
        self = self.with_context(**context)
        return super(SaleAdvancePaymentInv, self).create_invoices()

    def create_invoices(self):
        if not self.in_background and not self.invoice_batch_create:
            return super(SaleAdvancePaymentInv, self).create_invoices()

        invoice_batch = None
        if self.invoice_batch_create:
            invoice_batch = self.env["account.invoice.batch"].create(
                {
                    "date": fields.Datetime.now(),
                }
            )

        if self.in_background:
            sale_orders = self.env["sale.order"].browse(
                self._context.get("active_ids", [])
            )
            order_groups = {}
            for order in sale_orders:
                group_key = order._get_sale_invoicing_group_key()
                if group_key not in order_groups:
                    order_groups[group_key] = order
                else:
                    order_groups[group_key] += order

            for order_group in order_groups.values():
                self.with_delay().create_invoice_group(order_group, invoice_batch)

            res = {"type": "ir.actions.act_window_close"}
        else:
            if invoice_batch:
                self = self.with_context(batch_id=invoice_batch.id)
            res = super(SaleAdvancePaymentInv, self).create_invoices()

            invoices = self.env["account.move"].search(
                [("invoice_batch_id", "=", invoice_batch.id)]
            )
            if not invoices:
                raise UserError(_("There is no invoiceable line."))

        if self._context.get("open_batch", False):
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account_invoice_batches.account_invoice_batch_action"
            )
            action["views"] = [
                (
                    self.env.ref(
                        "account_invoice_batches.account_invoice_batch_view_form"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = invoice_batch.id

            return action

        return res

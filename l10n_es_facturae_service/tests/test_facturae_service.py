from odoo import fields
from odoo.tests import Form, common


class TestFacturaeService(common.SavepointCase):
    def test_facturae_data(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.env.ref("base.res_partner_1")
        with sale_order_form.order_line.new() as line_form:
            new_product = self.env.ref("product.product_product_1").copy(
                {"invoice_policy": "order"}
            )
            line_form.product_id = new_product
            line_form.save()
        self.sale_order = sale_order_form.save()

        self.sale_order.write(
            {
                "insured_ident_cardnum": "ABC",
                "policy_number": "123",
                "auth_number": "123456",
                "service_date": "2022-01-06",
            }
        )
        self.sale_order.action_confirm()
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=self.sale_order.ids, active_model="sale.order")
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()
        invoice = self.sale_order.invoice_ids[0]
        self.assertEqual(
            self.sale_order.insured_ident_cardnum,
            invoice.invoice_line_ids.mapped("facturae_file_reference")[0],
        )
        self.assertEqual(
            self.sale_order.policy_number,
            invoice.invoice_line_ids.mapped("facturae_receiver_transaction_reference")[
                0
            ],
        )
        self.assertEqual(
            self.sale_order.auth_number,
            invoice.invoice_line_ids.mapped("facturae_receiver_contract_reference")[0],
        )
        self.assertEqual(
            fields.Date.context_today(
                self.sale_order.with_context(tz=self.sale_order.create_uid.tz),
                self.sale_order.service_date,
            ),
            invoice.invoice_line_ids.mapped("facturae_receiver_transaction_date")[0],
        )

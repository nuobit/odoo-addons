# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mail.tests.common import MailCommon, mail_new_test_user

# a plain-text customer reply, formatted by MockEmail.format()
REPLY_TEMPLATE = """Return-Path: {return_path}
To: {to}
Cc: {cc}
From: {email_from}
Subject: {subject}
Date: Tue, 08 Sep 2026 14:16:26 +0000
Message-ID: {msg_id}
Content-Type: text/plain; charset=utf-8
{extra}

Received, thank you.
"""


class InvoiceBatchCommon(MailCommon):
    """Data shared by the invoice batch tests.

    It reproduces the real setup: an invoice batch user with the Billing group
    only, a launcher with sales and invoicing rights, a salesperson distinct
    from both, customers with and without a billing contact, a printed
    customer, a service product and a batch e-mail template sent from the
    invoice batch user's mailbox.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._activate_multi_company()
        cls.company = cls.company_admin
        cls.batch_user = mail_new_test_user(
            cls.env,
            login="invoice_batch_user",
            name="Billing Service",
            email="billing@test.example.com",
            groups="account.group_account_invoice",
            company_id=cls.company.id,
            company_ids=[(6, 0, cls.company.ids)],
            notification_type="email",
        )
        cls.launcher = mail_new_test_user(
            cls.env,
            login="invoice_batch_launcher",
            name="Batch Launcher",
            email="launcher@test.example.com",
            groups="sales_team.group_sale_salesman_all_leads,"
            "account.group_account_invoice",
            company_id=cls.company.id,
            company_ids=[(6, 0, cls.company.ids)],
            notification_type="email",
        )
        cls.salesperson = mail_new_test_user(
            cls.env,
            login="invoice_batch_salesperson",
            name="Order Salesperson",
            email="salesperson@test.example.com",
            groups="sales_team.group_sale_salesman",
            company_id=cls.company.id,
            company_ids=[(6, 0, cls.company.ids)],
            notification_type="email",
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Customer With Billing Contact",
                "email": "customer@test.example.com",
                "invoice_batch_sending_method": "email",
            }
        )
        cls.billing_contact = cls.env["res.partner"].create(
            {
                "name": "Customer Billing Contact",
                "parent_id": cls.customer.id,
                "email": "billing.contact@test.example.com",
            }
        )
        cls.customer.invoice_batch_email_partner_id = cls.billing_contact
        cls.customer_no_contact = cls.env["res.partner"].create(
            {
                "name": "Customer Without Billing Contact",
                "email": "customer2@test.example.com",
                "invoice_batch_sending_method": "email",
            }
        )
        cls.customer_pdf = cls.env["res.partner"].create(
            {
                "name": "Printed Customer",
                "email": "customer3@test.example.com",
                "invoice_batch_sending_method": "pdf",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Batch Service",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )
        cls.template = cls.env["mail.template"].create(
            {
                "name": "Invoice batch e-mail",
                "model_id": cls.env["ir.model"]._get_id("account.move"),
                "subject": "Invoice ${object.name}",
                "body_html": "<p>Please find attached the invoice ${object.name}.</p>",
                "email_from": '"Billing Service" <billing@test.example.com>',
                "partner_to": "${object.invoice_batch_email_partner_id.id}",
                "auto_delete": False,
            }
        )
        cls.company.write(
            {
                "invoice_batch_sending_email_template_id": cls.template.id,
                "invoice_batch_user_id": cls.batch_user.id,
                "report_service_id": cls.env.ref("account.account_invoices").id,
            }
        )

    @classmethod
    def _create_order(cls, partner):
        """Confirmed order of one service line, sold by the salesperson."""
        order = (
            cls.env["sale.order"]
            .with_user(cls.launcher)
            .create(
                {
                    "partner_id": partner.id,
                    "user_id": cls.salesperson.id,
                    "order_line": [
                        (0, 0, {"product_id": cls.product.id, "product_uom_qty": 1})
                    ],
                }
            )
        )
        order.action_confirm()
        return order

    def _batch_invoicing_wizard(
        self, orders, in_background, user=None, create_batch=True
    ):
        """The sale invoicing wizard opened on the orders, as the launcher."""
        return (
            self.env["sale.advance.payment.inv"]
            .with_user(user or self.launcher)
            .with_context(
                active_model="sale.order",
                active_ids=orders.ids,
                active_id=orders[:1].id,
            )
            .create(
                {
                    "advance_payment_method": "delivered",
                    "invoice_batch_create": create_batch,
                    "in_background": in_background,
                }
            )
        )

    def _batch_process_wizard(self, records, user=None, **values):
        """The batch processing wizard opened on batches or on invoices."""
        return (
            self.env["account.invoice.batch.process"]
            .with_user(user or self.launcher)
            .with_context(
                active_model=records._name,
                active_ids=records.ids,
                active_id=records[:1].id,
            )
            .create(values)
        )

    def _launch_batch(self, orders, in_background=False, user=None):
        """Launch the batch invoicing of the orders; return the batch created."""
        existing = self.env["account.invoice.batch"].search([])
        self._batch_invoicing_wizard(orders, in_background, user).create_invoices()
        batches = self.env["account.invoice.batch"].search(
            [("id", "not in", existing.ids)]
        )
        self.assertEqual(len(batches), 1)
        return batches

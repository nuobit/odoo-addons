# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import REPLY_TEMPLATE, InvoiceBatchCommon


class TestInvoiceBatchJobs(InvoiceBatchCommon):
    """The batch jobs run as the invoice batch user of the company.

    That user has the Billing group only: these tests passing proves that
    group, plus the access right the module gives it on the sale invoicing
    wizard, is enough to generate and e-mail the batch invoices.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orders = cls._create_order(cls.customer) + cls._create_order(
            cls.customer_no_contact
        )

    def _assert_invoices_belong_to_the_batch_user(self, invoices):
        self.assertEqual(len(invoices), 2)
        for invoice in invoices:
            self.assertEqual(invoice.create_uid, self.batch_user)
            self.assertIn(self.batch_user.partner_id, invoice.message_partner_ids)
            self.assertIn(self.salesperson.partner_id, invoice.message_partner_ids)
            self.assertNotIn(self.launcher.partner_id, invoice.message_partner_ids)
            self.assertEqual(
                invoice.message_ids.mapped("author_id"), self.batch_user.partner_id
            )

    def _sent_mail(self, invoice):
        mails = self.env["mail.mail"].search(
            [("model", "=", "account.move"), ("res_id", "=", invoice.id)]
        )
        self.assertEqual(len(mails), 1)
        return mails

    def test_background_invoicing_runs_as_the_batch_user(self):
        with trap_jobs() as trap:
            batch = self._launch_batch(self.orders, in_background=True)
            trap.assert_jobs_count(2)
            trap.perform_enqueued_jobs()
        self.assertEqual(batch.create_uid, self.launcher)
        self._assert_invoices_belong_to_the_batch_user(batch.invoice_ids)

    def test_synchronous_invoicing_runs_as_the_batch_user(self):
        batch = self._launch_batch(self.orders, in_background=False)
        self.assertEqual(batch.create_uid, self.launcher)
        self._assert_invoices_belong_to_the_batch_user(batch.invoice_ids)

    def test_background_invoicing_without_batch_keeps_the_launcher(self):
        with trap_jobs() as trap:
            self._batch_invoicing_wizard(
                self.orders, in_background=True, create_batch=False
            ).create_invoices()
            trap.assert_jobs_count(2)
            trap.perform_enqueued_jobs()
        invoices = self.orders.invoice_ids
        self.assertEqual(len(invoices), 2)
        self.assertFalse(invoices.mapped("invoice_batch_id"))
        self.assertEqual(invoices.mapped("create_uid"), self.launcher)
        for invoice in invoices:
            self.assertIn(self.launcher.partner_id, invoice.message_partner_ids)

    def test_plain_invoicing_keeps_the_launcher(self):
        self._batch_invoicing_wizard(
            self.orders, in_background=False, create_batch=False
        ).create_invoices()
        invoices = self.orders.invoice_ids
        self.assertEqual(len(invoices), 2)
        self.assertFalse(invoices.mapped("invoice_batch_id"))
        self.assertEqual(invoices.mapped("create_uid"), self.launcher)

    def test_send_email_runs_as_the_batch_user(self):
        batch = self._launch_batch(self.orders)
        batch.invoice_ids.action_post()
        followers_before = {
            invoice: invoice.message_partner_ids for invoice in batch.invoice_ids
        }
        with self.mock_mail_gateway(), trap_jobs() as trap:
            self._batch_process_wizard(
                batch, invoice_batch_sending_pdf=False
            ).process_invoices()
            trap.assert_jobs_count(2)
            trap.perform_enqueued_jobs()
        for invoice in batch.invoice_ids:
            self.assertTrue(invoice.is_move_sent)
            mail = self._sent_mail(invoice)
            self.assertEqual(mail.author_id, self.batch_user.partner_id)
            self.assertEqual(
                mail.email_from, '"Billing Service" <billing@test.example.com>'
            )
            self.assertEqual(invoice.message_partner_ids, followers_before[invoice])
            self.assertNotIn(self.launcher.partner_id, invoice.message_partner_ids)
        invoice_with_contact = batch.invoice_ids.filtered(
            lambda inv: inv.partner_id == self.customer
        )
        self.assertEqual(
            self._sent_mail(invoice_with_contact).recipient_ids, self.billing_contact
        )

    def test_customer_reply_notifies_the_batch_user_not_the_launcher(self):
        batch = self._launch_batch(self.orders)
        batch.invoice_ids.action_post()
        invoice = batch.invoice_ids.filtered(
            lambda inv: inv.partner_id == self.customer
        )
        with self.mock_mail_gateway(), trap_jobs() as trap:
            self._batch_process_wizard(
                batch, invoice_batch_sending_pdf=False
            ).process_invoices()
            trap.perform_enqueued_jobs()
            sent = self._sent_mail(invoice)
            self.format_and_process(
                REPLY_TEMPLATE,
                self.billing_contact.email_formatted,
                sent.reply_to,
                subject="Re: %s" % sent.subject,
                extra="In-Reply-To: %s" % sent.message_id,
                target_model="account.move",
                target_field="name",
            )
        reply = invoice.message_ids.filtered(
            lambda msg: msg.author_id == self.billing_contact
        )
        self.assertEqual(len(reply), 1)
        notified = [address for mail in self._mails for address in mail["email_to"]]
        self.assertTrue(any(self.batch_user.email in to for to in notified))
        self.assertFalse(any(self.launcher.email in to for to in notified))

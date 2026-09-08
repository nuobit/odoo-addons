# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import InvoiceBatchCommon


class TestInvoiceBatchRecipient(InvoiceBatchCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orders = cls._create_order(cls.customer) + cls._create_order(
            cls.customer_no_contact
        )

    def test_recipient_is_the_contact_or_the_partner(self):
        batch = self._launch_batch(self.orders)
        for invoice in batch.invoice_ids:
            if invoice.partner_id == self.customer:
                self.assertEqual(
                    invoice.invoice_batch_email_recipient_id, self.billing_contact
                )
            elif invoice.partner_id == self.customer_no_contact:
                self.assertEqual(
                    invoice.invoice_batch_email_recipient_id, self.customer_no_contact
                )
            else:
                self.fail("unexpected invoice partner %s" % invoice.partner_id.name)

    def test_entry_without_partner_has_no_recipient(self):
        entry = self.env["account.move"].create({"move_type": "entry"})
        self.assertFalse(entry.partner_id)
        self.assertFalse(entry.invoice_batch_email_recipient_id)

    def test_template_addresses_the_recipient(self):
        batch = self._launch_batch(self.orders)
        for invoice in batch.invoice_ids:
            values = self.template.generate_email(invoice.ids, ["partner_to"])
            self.assertEqual(
                values[invoice.id]["partner_ids"],
                invoice.invoice_batch_email_recipient_id.ids,
            )

    def test_contact_that_is_an_internal_partner_gets_the_email(self):
        """A cash customer's batch e-mail goes to the billing mailbox itself."""
        batch = self._launch_batch(self._create_order(self.customer_cash))
        invoice = batch.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            invoice.invoice_batch_email_recipient_id, self.batch_user.partner_id
        )
        invoice.action_post()
        with self.mock_mail_gateway(), trap_jobs() as trap:
            self._batch_process_wizard(
                batch, invoice_batch_sending_pdf=False
            ).process_invoices()
            trap.assert_jobs_count(1)
            trap.perform_enqueued_jobs()
        mails = self.env["mail.mail"].search(
            [("model", "=", "account.move"), ("res_id", "=", invoice.id)]
        )
        self.assertEqual(len(mails), 1)
        self.assertEqual(mails.author_id, self.batch_user.partner_id)
        self.assertEqual(mails.recipient_ids, self.batch_user.partner_id)
        self.assertTrue(invoice.is_move_sent)

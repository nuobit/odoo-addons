# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import InvoiceBatchCommon


class TestInvoiceBatchChatter(InvoiceBatchCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orders = (
            cls._create_order(cls.customer)
            + cls._create_order(cls.customer_no_contact)
            + cls._create_order(cls.customer_pdf)
        )

    def _launch_notes(self, batch):
        return batch.message_ids.filtered(
            lambda msg: "Batch processing launched" in msg.body
        )

    def test_launcher_follows_the_batch(self):
        batch = self._launch_batch(self.orders)
        self.assertEqual(batch.create_uid, self.launcher)
        self.assertIn(self.launcher.partner_id, batch.message_partner_ids)

    def test_processing_a_batch_posts_one_note_with_the_counts(self):
        batch = self._launch_batch(self.orders)
        batch.invoice_ids.with_user(self.launcher).action_post()
        with trap_jobs():
            self._batch_process_wizard(batch).process_invoices()
        note = self._launch_notes(batch)
        self.assertEqual(len(note), 1)
        self.assertEqual(note.author_id, self.launcher.partner_id)
        self.assertEqual(note.subtype_id, self.env.ref("mail.mt_note"))
        self.assertIn("1 PDF, 2 e-mail", note.body)

    def test_processing_invoices_posts_one_note_per_batch(self):
        batch_email = self._launch_batch(self.orders[:2])
        batch_pdf = self._launch_batch(self.orders[2:])
        invoices = (batch_email + batch_pdf).invoice_ids
        invoices.with_user(self.launcher).action_post()
        with trap_jobs():
            self._batch_process_wizard(invoices).process_invoices()
        note_email = self._launch_notes(batch_email)
        self.assertEqual(len(note_email), 1)
        self.assertIn("2 e-mail", note_email.body)
        self.assertNotIn("PDF", note_email.body)
        note_pdf = self._launch_notes(batch_pdf)
        self.assertEqual(len(note_pdf), 1)
        self.assertIn("1 PDF", note_pdf.body)
        self.assertNotIn("e-mail", note_pdf.body)

    def test_processing_with_no_method_enabled_posts_no_note(self):
        batch = self._launch_batch(self.orders)
        batch.invoice_ids.with_user(self.launcher).action_post()
        with trap_jobs() as trap:
            self._batch_process_wizard(
                batch,
                invoice_batch_sending_pdf=False,
                invoice_batch_sending_email=False,
                invoice_batch_sending_signedfacturae=False,
                invoice_batch_sending_unsignedfacturae=False,
            ).process_invoices()
        trap.assert_jobs_count(0)
        self.assertFalse(self._launch_notes(batch))

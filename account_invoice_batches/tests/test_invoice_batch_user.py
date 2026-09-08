# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import InvoiceBatchCommon


class TestInvoiceBatchUser(InvoiceBatchCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orders = (
            cls._create_order(cls.customer)
            + cls._create_order(cls.customer_no_contact)
            + cls._create_order(cls.customer_pdf)
        )

    def _assert_launch_blocked(self, in_background):
        """The launch fails naming the company before any batch, job or invoice."""
        batches_before = self.env["account.invoice.batch"].search([])
        with trap_jobs() as trap, self.assertRaises(UserError) as error:
            self._batch_invoicing_wizard(self.orders, in_background).create_invoices()
        self.assertIn(self.company.name, str(error.exception))
        trap.assert_jobs_count(0)
        self.assertEqual(self.env["account.invoice.batch"].search([]), batches_before)
        self.assertFalse(self.orders.invoice_ids)

    def _posted_batch(self):
        """A batch of the three orders with its invoices posted, e-mails unsent."""
        batch = self._launch_batch(self.orders)
        batch.invoice_ids.action_post()
        self.assertEqual(len(batch.unsent_invoice_ids), 3)
        return batch

    def test_settings_store_the_invoice_batch_user(self):
        self.company.invoice_batch_user_id = False
        settings = (
            self.env["res.config.settings"]
            .with_user(self.user_admin)
            .create({"invoice_batch_user_id": self.batch_user.id})
        )
        settings.execute()
        self.assertEqual(self.company.invoice_batch_user_id, self.batch_user)

    def test_settings_refuse_a_portal_user(self):
        portal = self._create_portal_user()
        with self.assertRaises(ValidationError):
            self.env["res.config.settings"].with_user(self.user_admin).create(
                {"invoice_batch_user_id": portal.id}
            ).execute()
        self.assertEqual(self.company.invoice_batch_user_id, self.batch_user)

    def test_launch_with_user_turned_portal_is_blocked(self):
        self.batch_user.write(
            {"groups_id": [(6, 0, self.env.ref("base.group_portal").ids)]}
        )
        self.assertTrue(self.batch_user.share)
        self._assert_launch_blocked(in_background=True)

    def test_launch_without_invoice_batch_user_is_blocked(self):
        self.company.invoice_batch_user_id = False
        self._assert_launch_blocked(in_background=True)
        self._assert_launch_blocked(in_background=False)

    def test_launch_with_archived_user_is_blocked(self):
        self.batch_user.action_archive()
        self._assert_launch_blocked(in_background=True)

    def test_launch_with_user_without_email_is_blocked(self):
        self.batch_user.email = False
        self._assert_launch_blocked(in_background=True)

    def test_launch_with_user_not_allowed_on_company_is_blocked(self):
        self.batch_user.write(
            {
                "company_id": self.company_2.id,
                "company_ids": [(6, 0, self.company_2.ids)],
            }
        )
        self._assert_launch_blocked(in_background=True)

    def test_launch_with_orders_of_another_company_is_blocked(self):
        self.launcher.write({"company_ids": [(4, self.company_2.id)]})
        foreign_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "company_id": self.company_2.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1})
                ],
            }
        )
        batches_before = self.env["account.invoice.batch"].search([])
        with trap_jobs() as trap, self.assertRaises(UserError) as error:
            self._batch_invoicing_wizard(
                self.orders + foreign_order, in_background=True
            ).create_invoices()
        self.assertIn(self.company.name, str(error.exception))
        trap.assert_jobs_count(0)
        self.assertEqual(self.env["account.invoice.batch"].search([]), batches_before)
        self.assertFalse(self.orders.invoice_ids)

    def test_launch_without_orders_is_blocked(self):
        with self.assertRaises(UserError):
            self._batch_invoicing_wizard(
                self.env["sale.order"], in_background=True
            ).create_invoices()

    def test_launch_in_background_queues_one_job_per_invoicing_group(self):
        with trap_jobs() as trap:
            batch = self._launch_batch(self.orders, in_background=True)
            trap.assert_jobs_count(3)
            self.assertFalse(batch.invoice_ids)
            trap.perform_enqueued_jobs()
        self.assertEqual(len(batch.invoice_ids), 3)
        self.assertEqual(self.orders.invoice_ids, batch.invoice_ids)
        self.assertEqual(
            batch.invoice_ids.mapped("partner_id"), self.orders.mapped("partner_id")
        )

    def test_launch_synchronously_creates_the_batch_invoices(self):
        with trap_jobs() as trap:
            batch = self._launch_batch(self.orders, in_background=False)
        trap.assert_jobs_count(0)
        self.assertEqual(len(batch.invoice_ids), 3)
        self.assertEqual(self.orders.invoice_ids, batch.invoice_ids)
        self.assertEqual(
            batch.invoice_ids.mapped("invoice_batch_sending_method"),
            self.orders.mapped("partner_id.invoice_batch_sending_method"),
        )

    def test_invoice_group_job_without_user_is_blocked(self):
        with trap_jobs() as trap:
            batch = self._launch_batch(self.orders, in_background=True)
            trap.assert_jobs_count(3)
            self.company.invoice_batch_user_id = False
            with self.assertRaises(UserError) as error:
                trap.perform_enqueued_jobs()
        self.assertIn(self.company.name, str(error.exception))
        self.assertFalse(batch.invoice_ids)

    def test_process_with_email_without_user_is_blocked(self):
        batch = self._posted_batch()
        self.company.invoice_batch_user_id = False
        for records in (batch, batch.invoice_ids):
            with trap_jobs() as trap, self.assertRaises(UserError) as error:
                self._batch_process_wizard(records).process_invoices()
            self.assertIn(self.company.name, str(error.exception))
            trap.assert_jobs_count(0)
            self.assertFalse(any(batch.invoice_ids.mapped("is_move_sent")))

    def test_process_without_email_does_not_need_the_user(self):
        batch = self._posted_batch()
        self.company.invoice_batch_user_id = False
        with trap_jobs() as trap:
            action = self._batch_process_wizard(
                batch, invoice_batch_sending_email=False
            ).process_invoices()
        trap.assert_jobs_count(0)
        self.assertEqual(action["type"], "ir.actions.report")
        printed = batch.invoice_ids.filtered(
            lambda inv: inv.invoice_batch_sending_method == "pdf"
        )
        self.assertEqual(len(printed), 1)
        self.assertTrue(printed.is_move_sent)
        self.assertFalse(any((batch.invoice_ids - printed).mapped("is_move_sent")))

    def test_send_email_job_without_user_is_blocked(self):
        batch = self._posted_batch()
        with trap_jobs() as trap:
            self._batch_process_wizard(
                batch, invoice_batch_sending_pdf=False
            ).process_invoices()
            trap.assert_jobs_count(2)
            self.company.invoice_batch_user_id = False
            with self.assertRaises(UserError) as error:
                trap.perform_enqueued_jobs()
        self.assertIn(self.company.name, str(error.exception))
        self.assertFalse(any(batch.invoice_ids.mapped("is_move_sent")))

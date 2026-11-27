# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import InvoiceBatchCommon


class TestInvoiceBatchFollowers(InvoiceBatchCommon):
    """At validation, the customer follower of a batch invoice is its contact."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orders = (
            cls._create_order(cls.customer)
            + cls._create_order(cls.customer_self)
            + cls._create_order(cls.customer_no_contact)
        )

    def _batch_invoice(self, batch, partner):
        invoice = batch.invoice_ids.filtered(lambda inv: inv.partner_id == partner)
        self.assertEqual(len(invoice), 1)
        return invoice

    def _posted_batch_invoice(self, batch, partner):
        invoice = self._batch_invoice(batch, partner)
        invoice.with_user(self.launcher).action_post()
        return invoice

    def test_contact_replaces_the_partner_as_follower(self):
        batch = self._launch_batch(self.orders)
        invoice = self._posted_batch_invoice(batch, self.customer)
        self.assertIn(self.billing_contact, invoice.message_partner_ids)
        self.assertNotIn(self.customer, invoice.message_partner_ids)
        self.assertIn(self.batch_user.partner_id, invoice.message_partner_ids)

    def test_contact_equal_to_the_partner_keeps_the_partner(self):
        batch = self._launch_batch(self.orders)
        invoice = self._posted_batch_invoice(batch, self.customer_self)
        self.assertIn(self.customer_self, invoice.message_partner_ids)

    def test_no_contact_keeps_the_partner(self):
        batch = self._launch_batch(self.orders)
        invoice = self._posted_batch_invoice(batch, self.customer_no_contact)
        self.assertIn(self.customer_no_contact, invoice.message_partner_ids)

    def test_partner_subscribed_by_hand_stays_and_the_contact_is_not_added(self):
        batch = self._launch_batch(self.orders)
        invoice = self._batch_invoice(batch, self.customer)
        invoice.with_user(self.launcher).message_subscribe(
            partner_ids=self.customer.ids
        )
        invoice.with_user(self.launcher).action_post()
        self.assertIn(self.customer, invoice.message_partner_ids)
        self.assertNotIn(self.billing_contact, invoice.message_partner_ids)

    def test_invoice_outside_a_batch_keeps_the_native_follower(self):
        invoice = (
            self.env["account.move"]
            .with_user(self.launcher)
            .create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.customer.id,
                    "invoice_batch_email_partner_id": self.billing_contact.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "quantity": 1,
                                "price_unit": 100.0,
                            },
                        )
                    ],
                }
            )
        )
        invoice.action_post()
        self.assertFalse(invoice.invoice_batch_id)
        self.assertIn(self.customer, invoice.message_partner_ids)
        self.assertNotIn(self.billing_contact, invoice.message_partner_ids)

    def test_subscribing_the_partner_outside_validation_is_native(self):
        batch = self._launch_batch(self.orders)
        invoice = self._batch_invoice(batch, self.customer)
        invoice.with_user(self.launcher).message_subscribe(
            partner_ids=self.customer.ids
        )
        self.assertIn(self.customer, invoice.message_partner_ids)
        self.assertNotIn(self.billing_contact, invoice.message_partner_ids)

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged

from odoo.addons.connector_lengow.components.adapter import ConnectorLengowAdapter
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("post_install", "-at_install")
class TestOrderImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # The repo CI installs every module of the repo in a single
        # database, so sibling modules' partner constraints apply to the
        # partners this suite creates (e.g. email/mobile required, lang
        # required). Satisfy them through the real flow: partners carry an
        # email, and the addresses are French so their country resolves to
        # an installed, active language -- the actual Novolux marketplace
        # case.
        cls.env["res.lang"]._activate_lang("fr_FR")
        cls.backend = cls.env["lengow.backend"].create(
            {
                "name": "Lengow test backend",
                "access_token": "test-access-token",
                "secret": "test-secret",
                "lang_ids": [Command.link(cls.env.ref("base.lang_en").id)],
            }
        )
        cls.marketplace_partner = cls.env["res.partner"].create(
            {
                "name": "Test marketplace parent",
                "country_id": cls.env.ref("base.fr").id,
                "email": "marketplace.parent@example.com",
            }
        )
        cls.marketplace_map = cls.env["lengow.backend.marketplace"].create(
            {
                "backend_id": cls.backend.id,
                "partner_id": cls.marketplace_partner.id,
                "lengow_marketplace": "mkplace_test",
            }
        )
        product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "default_code": "SKU-1",
            }
        )
        cls.env["lengow.product.product"].create(
            {
                "backend_id": cls.backend.id,
                "odoo_id": product.id,
                "lengow_sku": "SKU-1",
            }
        )

    def _address(self, address_type, names):
        return {
            "type": address_type,
            "society": "",
            "civility": "",
            "email": "buyer@example.com",
            "phone_home": "",
            "phone_mobile": "",
            "first_line": "1 Test Street",
            "second_line": "",
            "zipcode": "75001",
            "city": "Test City",
            "common_country_iso_a2": "FR",
            **names,
        }

    def _order_payload(self, order_ref, billing_names, delivery_names):
        delivery_address = self._address("delivery", delivery_names)
        delivery_address["trackings"] = []
        return {
            "marketplace": "mkplace_test",
            "marketplace_order_id": order_ref,
            "lengow_status": "shipped",
            "marketplace_status": "shipped",
            "anonymized": False,
            "marketplace_order_date": "2026-06-01T10:00:00Z",
            "imported_at": "2026-06-01T10:00:00.000000Z",
            "updated_at": "2026-06-01T10:00:00.000000Z",
            "total_tax": "0.00",
            "commission": "0.00",
            "original_total_tax": "0.00",
            "original_commission": "0.00",
            "shipping": 0,
            "billing_address": self._address("billing", billing_names),
            "packages": [
                {
                    "cart": [
                        {
                            "id": 1001,
                            "merchant_product_id": {"id": "SKU-1"},
                            "marketplace_product_id": "MP-1",
                            "quantity": 1,
                            "amount": "10.00",
                            "tax": "0.00",
                            "original_amount": "10.00",
                            "original_tax": "0.00",
                        }
                    ],
                    "delivery": delivery_address,
                }
            ],
        }

    def _get_order(self, order_ref):
        return self.env["lengow.sale.order"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("lengow_marketplace_order_id", "=", order_ref),
            ]
        )

    def _get_buyer_partners(self):
        return self.env["res.partner"].search([("email", "=", "buyer@example.com")])

    def _run_import(self, payload):
        """Import one order through the real user flow.

        Backend import button -> the batch fetches and prepares the
        orders -> one job per order, carrying its prepared data, with the
        Lengow HTTP API mocked at its single entry point (_exec).
        """
        self.backend.import_sale_orders_order_number = payload["marketplace_order_id"]
        with mock.patch.object(
            ConnectorLengowAdapter, "_exec", return_value=[payload]
        ), trap_jobs() as trap:
            self.backend.import_sale_orders_since()
            trap.perform_enqueued_jobs()

    def test_first_last_source_ignores_full_name_updates(self):
        """With first_last source, full_name is ignored and a re-sync that
        rewrites it (e.g. with a carrier label) keeps the same partners."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        self._run_import(self._order_payload("TEST-1", person, person))
        binding = self._get_order("TEST-1")
        self.assertEqual(len(binding), 1)
        order = binding.odoo_id
        self.assertEqual(order.state, "sale")
        self.assertEqual(order.partner_shipping_id.name, "Jane Doe")
        self.assertEqual(order.partner_invoice_id.name, "Jane Doe")
        self.assertEqual(order.partner_id, self.marketplace_partner)
        partners_before = self._get_buyer_partners()
        shipping_before = order.partner_shipping_id
        # late re-sync of the same order: the marketplace rewrote the
        # delivery full_name with a carrier label
        relabeled = dict(person, full_name="CARRIER RELAY SERVICE")
        self._run_import(self._order_payload("TEST-1", person, relabeled))
        self.assertEqual(self._get_order("TEST-1"), binding)
        self.assertEqual(order.partner_shipping_id, shipping_before)
        self.assertEqual(self._get_buyer_partners(), partners_before)
        self.assertFalse(
            self.env["res.partner"].search([("name", "=", "CARRIER RELAY SERVICE")])
        )

    def test_full_name_source(self):
        """With full_name source, the name is read from full_name even when
        first/last name come empty."""
        self.marketplace_map.name_source = "full_name"
        alias = {"full_name": "Marketplace Alias", "first_name": "", "last_name": ""}
        self._run_import(self._order_payload("TEST-2", alias, alias))
        binding = self._get_order("TEST-2")
        self.assertEqual(len(binding), 1)
        order = binding.odoo_id
        self.assertEqual(order.state, "sale")
        self.assertEqual(order.partner_shipping_id.name, "Marketplace Alias")
        self.assertEqual(order.partner_invoice_id.name, "Marketplace Alias")

    def test_configured_source_empty_fails_order(self):
        """A marketplace publishing names only in full_name fails loudly
        under the first_last source, telling the user how to reconfigure."""
        alias = {"full_name": "Marketplace Alias", "first_name": "", "last_name": ""}
        with self.assertRaisesRegex(ValidationError, "Contact name source") as cm:
            self._run_import(self._order_payload("TEST-3", alias, alias))
        self.assertIn("TEST-3", str(cm.exception))
        self.assertIn("mkplace_test", str(cm.exception))
        self.assertIn("full_name is filled", str(cm.exception))
        self.assertIn("first_name is empty", str(cm.exception))
        self.assertFalse(self._get_order("TEST-3"))
        self.assertFalse(self._get_buyer_partners())

    def test_all_name_fields_empty_fails_order(self):
        """An order with no name anywhere fails under any configuration."""
        self.marketplace_map.name_source = "full_name"
        empty = {"full_name": "", "first_name": "", "last_name": ""}
        with self.assertRaisesRegex(ValidationError, "Contact name source") as cm:
            self._run_import(self._order_payload("TEST-4", empty, empty))
        self.assertIn("full_name is empty", str(cm.exception))
        self.assertIn("last_name is empty", str(cm.exception))
        self.assertFalse(self._get_order("TEST-4"))
        self.assertFalse(self._get_buyer_partners())

    def test_empty_name_error_states_order_age_and_anonymization(self):
        """A first import with no contact name anywhere also states the
        order date and age and explains that on old orders the likely
        cause is marketplace anonymization (GDPR), unrecoverable from
        Lengow -- the reader judges from the age."""
        self.marketplace_map.name_source = "full_name"
        empty = {"full_name": "", "first_name": "", "last_name": ""}
        payload = self._order_payload("TEST-11", empty, empty)
        payload["marketplace_order_date"] = "2024-04-16T10:00:00Z"
        with self.assertRaisesRegex(ValidationError, "Contact name source") as cm:
            self._run_import(payload)
        self.assertIn("2024-04-16", str(cm.exception))
        self.assertIn("days ago", str(cm.exception))
        self.assertIn("(GDPR)", str(cm.exception))
        self.assertIn("cannot be recovered", str(cm.exception))
        self.assertFalse(self._get_order("TEST-11"))
        self.assertFalse(self._get_buyer_partners())

    def test_reconfigure_and_reimport_heals(self):
        """The remediation the error message instructs: wrong source ->
        the job fails with the hint -> fix the mapping -> import the order
        again. Requeuing the old job is NOT enough: it carries the data
        prepared at download time."""
        alias = {"full_name": "Marketplace Alias", "first_name": "", "last_name": ""}
        payload = self._order_payload("TEST-8", alias, alias)
        self.backend.import_sale_orders_order_number = "TEST-8"
        with mock.patch.object(
            ConnectorLengowAdapter, "_exec", return_value=[payload]
        ), trap_jobs() as trap:
            self.backend.import_sale_orders_since()
            trap.assert_jobs_count(1)
            job = trap.enqueued_jobs[0]
            with self.assertRaisesRegex(ValidationError, "Contact name source"):
                job.perform()
            self.marketplace_map.name_source = "full_name"
            with self.assertRaisesRegex(ValidationError, "Contact name source"):
                job.perform()
        self.assertFalse(self._get_order("TEST-8"))
        self._run_import(self._order_payload("TEST-8", alias, alias))
        binding = self._get_order("TEST-8")
        self.assertEqual(len(binding), 1)
        self.assertEqual(binding.odoo_id.partner_shipping_id.name, "Marketplace Alias")

    def test_marketplace_without_mapping_fails_only_its_job(self):
        """An order of a not-yet-mapped marketplace must not break the
        batch fetch: it fails its own job asking to add the mapping."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        payload = self._order_payload("TEST-7", person, person)
        payload["marketplace"] = "mkplace_unmapped"
        self.backend.import_sale_orders_order_number = "TEST-7"
        with mock.patch.object(
            ConnectorLengowAdapter, "_exec", return_value=[payload]
        ), trap_jobs() as trap:
            self.backend.import_sale_orders_since()
            trap.assert_jobs_count(1)
            with self.assertRaisesRegex(ValidationError, "add it on backend mappings"):
                trap.perform_enqueued_jobs()
        self.assertFalse(self._get_order("TEST-7"))
        self.assertFalse(self._get_buyer_partners())

    def test_anonymized_resync_keeps_partners(self):
        """A late re-sync of an already-imported order whose contact names
        were erased upstream (GDPR anonymization) must not fail the job:
        the update proceeds and the order keeps the partners of the
        original import. Nobody can bring the erased name back, so a
        failure here would stay red forever."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        self._run_import(self._order_payload("TEST-9", person, person))
        binding = self._get_order("TEST-9")
        self.assertEqual(len(binding), 1)
        order = binding.odoo_id
        partners_before = self._get_buyer_partners()
        shipping_before = order.partner_shipping_id
        invoice_before = order.partner_invoice_id
        erased = {"full_name": "", "first_name": "", "last_name": ""}
        payload = self._order_payload("TEST-9", erased, erased)
        payload["marketplace_status"] = "closed"
        self._run_import(payload)
        # the re-sync went through: the status update landed...
        self.assertEqual(binding.marketplace_status, "closed")
        # ...and the partners stayed exactly as originally imported
        self.assertEqual(order.partner_shipping_id, shipping_before)
        self.assertEqual(order.partner_invoice_id, invoice_before)
        self.assertEqual(self._get_buyer_partners(), partners_before)

    def test_partially_anonymized_resync(self):
        """Each address is judged on its own: a re-sync erasing only the
        delivery contact name skips only that partner; the billing one
        follows the normal flow."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        self._run_import(self._order_payload("TEST-10", person, person))
        binding = self._get_order("TEST-10")
        self.assertEqual(len(binding), 1)
        order = binding.odoo_id
        partners_before = self._get_buyer_partners()
        shipping_before = order.partner_shipping_id
        invoice_before = order.partner_invoice_id
        erased = {"full_name": "", "first_name": "", "last_name": ""}
        self._run_import(self._order_payload("TEST-10", person, erased))
        self.assertEqual(order.partner_shipping_id, shipping_before)
        self.assertEqual(order.partner_invoice_id, invoice_before)
        self.assertEqual(self._get_buyer_partners(), partners_before)

    def test_import_record_without_external_data_reads_backend(self):
        """import_record without external_data falls back to the adapter
        read() (e.g. a manual single-order import) and imports normally."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        payload = self._order_payload("TEST-5", person, person)
        with mock.patch.object(ConnectorLengowAdapter, "_exec", return_value=[payload]):
            self.env["lengow.sale.order"].import_record(
                self.backend, ["mkplace_test", "TEST-5"], fields.Datetime.now()
            )
        binding = self._get_order("TEST-5")
        self.assertEqual(len(binding), 1)
        self.assertEqual(binding.odoo_id.state, "sale")
        self.assertEqual(binding.odoo_id.partner_shipping_id.name, "Jane Doe")

    def test_read_multiple_records_for_unique_key_fails(self):
        """The adapter read() rejects a backend answer with more than one
        record for the unique key instead of picking one silently."""
        person = {"full_name": "", "first_name": "Jane", "last_name": "Doe"}
        duplicated = [
            self._order_payload("TEST-6", person, person),
            self._order_payload("TEST-6", person, person),
        ]
        with mock.patch.object(
            ConnectorLengowAdapter, "_exec", return_value=duplicated
        ), self.assertRaisesRegex(ValidationError, "more than 1 record"):
            self.env["lengow.sale.order"].import_record(
                self.backend, ["mkplace_test", "TEST-6"], fields.Datetime.now()
            )
        self.assertFalse(self._get_order("TEST-6"))

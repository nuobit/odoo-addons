# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged

from odoo.addons.connector_lengow.components.adapter import ConnectorLengowAdapter


@tagged("post_install", "-at_install")
class TestOrderImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
                "country_id": cls.env.ref("base.us").id,
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
            "zipcode": "10001",
            "city": "Test City",
            "common_country_iso_a2": "US",
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

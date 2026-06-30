# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderSequence(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.normal_sale_type = cls.env.ref("sale_order_type.normal_sale_type")
        cls.rental_sale_type = cls.env.ref("rental_base.rental_sale_type")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Sequence Partner",
            }
        )

    def _expected_name(self, sequence):
        return sequence.get_next_char(sequence.number_next_actual)

    def test_explicit_normal_type_uses_normal_sequence_with_rental_context(self):
        expected_name = self._expected_name(self.normal_sale_type.sequence_id)
        order = (
            self.env["sale.order"]
            .with_context(default_type_id=self.rental_sale_type.id)
            .create(
                {
                    "type_id": self.normal_sale_type.id,
                    "partner_id": self.partner.id,
                }
            )
        )
        self.assertEqual(order.type_id, self.normal_sale_type)
        self.assertEqual(order.name, expected_name)
        self.assertFalse(order.is_rental_order)

    def test_resolved_normal_type_uses_normal_sequence_with_rental_context(self):
        self.partner.with_company(self.env.company).sale_type = self.normal_sale_type
        expected_name = self._expected_name(self.normal_sale_type.sequence_id)
        order = (
            self.env["sale.order"]
            .with_context(default_type_id=self.rental_sale_type.id)
            .create({"partner_id": self.partner.id})
        )
        self.assertEqual(order.type_id, self.normal_sale_type)
        self.assertEqual(order.name, expected_name)
        self.assertFalse(order.is_rental_order)

    def test_rental_default_type_uses_rental_sequence(self):
        expected_name = self._expected_name(self.rental_sale_type.sequence_id)
        order = (
            self.env["sale.order"]
            .with_context(default_type_id=self.rental_sale_type.id)
            .create({"partner_id": self.partner.id})
        )
        self.assertEqual(order.type_id, self.rental_sale_type)
        self.assertEqual(order.name, expected_name)
        self.assertTrue(order.is_rental_order)

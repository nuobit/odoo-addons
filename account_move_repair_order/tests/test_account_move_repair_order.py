# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestAccountMoveRepairOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.account_move_model = self.env["account.move"]
        self.repair_order_model = self.env["repair.order"]

    def test_repair_order_field_exists(self):
        """Test that repair_order_id field exists on account.move"""
        self.assertTrue(
            hasattr(self.account_move_model, "repair_order_id"),
            "repair_order_id field should exist on account.move",
        )

    def test_invoice_ids_field_exists(self):
        """Test that invoice_ids field exists on repair.order"""
        self.assertTrue(
            hasattr(self.repair_order_model, "invoice_ids"),
            "invoice_ids field should exist on repair.order",
        )

    def test_field_relationship(self):
        """Test that fields have correct relationship configuration"""
        repair_order_field = self.account_move_model._fields.get("repair_order_id")
        self.assertEqual(
            repair_order_field.comodel_name,
            "repair.order",
            "repair_order_id should point to repair.order",
        )

        invoice_ids_field = self.repair_order_model._fields.get("invoice_ids")
        self.assertEqual(
            invoice_ids_field.comodel_name,
            "account.move",
            "invoice_ids should point to account.move",
        )
        self.assertEqual(
            invoice_ids_field.inverse_name,
            "repair_order_id",
            "invoice_ids should have correct inverse_name",
        )

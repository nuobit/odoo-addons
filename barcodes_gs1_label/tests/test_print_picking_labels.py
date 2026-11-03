# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError

from .common import TestCommon


class TestPrintPickingLabels(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.uom_gram = cls.env.ref("uom.product_uom_gram")
        # receipt labels print the weight received
        cls.config_gs1_128.show_weight = True

    def test_receipt_in_units_prints_one_label_per_unit(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.uom_unit.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        receipt.move_ids.move_line_ids.lot_name = "LOT-A"
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A", "(01)02000000000015(10)LOT-A"],
        )

    def test_receipt_in_kg_prints_one_label_with_the_received_weight(self):
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 12.5,
                            "product_uom": self.uom_kg.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3101)000125"]
        )

    def _receive(self, product, quantity, uom):
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                            "product_uom": uom.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        receipt.button_validate()
        return receipt

    def test_receipt_in_grams_prints_the_received_weight_in_kg(self):
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_gram.id,
            uom_po_id=self.uom_gram.id,
        )
        receipt = self._receive(product, 500, self.uom_gram)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3101)000005"]
        )

    def test_receipt_in_units_prints_the_weight_of_the_product(self):
        product = self._create_product("Product", "2000000000015", weight=2.5)
        receipt = self._receive(product, 1, self.uom_unit)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3101)000025"]
        )

    def test_receipt_in_units_prints_a_weight_in_pounds_in_kg(self):
        self.env["ir.config_parameter"].set_param("product.weight_in_lbs", "1")
        product = self._create_product("Product", "2000000000015", weight=1)
        receipt = self._receive(product, 1, self.uom_unit)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 1 lb in kg, rounded to the five decimals the AI holds
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3105)045359"]
        )

    def test_receipt_in_kg_without_the_weight_option_prints_no_weight(self):
        self.config_gs1_128.show_weight = False
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        receipt = self._receive(product, 12.5, self.uom_kg)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(self._get_label_texts(report_action), ["(01)02000000000015"])

    def test_receipt_not_done_raises(self):
        product = self._create_product("Product", "2000000000015")
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.uom_unit.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        with self.assertRaisesRegex(UserError, "There are no done move lines"):
            self._render_labels(report_action)

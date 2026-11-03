# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.barcodes_gs1_label.tests.common import TestCommon


class TestPrintPickingLabels(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.uom_gram = cls.env.ref("uom.product_uom_gram")
        # receipt labels print the weight received
        cls.config_gs1_128.show_weight = True

    def _purchase(self, product, quantity, uom):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": quantity,
                            "product_uom": uom.id,
                        }
                    )
                ],
            }
        )
        purchase.button_confirm()
        return purchase.picking_ids

    def _create_dynamic_uom(self, name="Piece", ratio=1):
        # its kilos per unit are known only when the goods are received
        return self.env["uom.uom"].create(
            {
                "name": name,
                "category_id": self.uom_kg.category_id.id,
                "uom_type": "bigger",
                "ratio": ratio,
                "dynamic_ratio": True,
            }
        )

    def test_purchase_receipt_in_units_prints_one_label_per_unit(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        receipt = self._purchase(product, 2, self.uom_unit)
        receipt.move_ids.move_line_ids.lot_name = "LOT-A"
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A", "(01)02000000000015(10)LOT-A"],
        )

    def test_purchase_in_a_dynamic_unit_prints_one_label_per_purchased_unit(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 3, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 7.5, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-A(3101)000025",
            ],
        )

    def test_purchase_of_25_kg_units_prints_one_label_per_unit_bought(self):
        uom_sack = self._create_dynamic_uom("Sack", 25)
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_sack.id,
        )
        receipt = self._purchase(product, 4, uom_sack)
        receipt.move_ids.move_line_ids.lot_name = "LOT-A"
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3100)000025",
                "(01)02000000000015(10)LOT-A(3100)000025",
                "(01)02000000000015(10)LOT-A(3100)000025",
                "(01)02000000000015(10)LOT-A(3100)000025",
            ],
        )

    def test_short_receipt_of_25_kg_units_shares_the_kilos_received(self):
        uom_sack = self._create_dynamic_uom("Sack", 25)
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_sack.id,
        )
        receipt = self._purchase(product, 4, uom_sack)
        receipt.move_ids.move_line_ids.write({"quantity": 98, "lot_name": "LOT-A"})
        receipt.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=receipt.ids
        ).button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 98 kg for the 4 sacks bought is 24.5 kg a sack
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)000245",
                "(01)02000000000015(10)LOT-A(3101)000245",
                "(01)02000000000015(10)LOT-A(3101)000245",
                "(01)02000000000015(10)LOT-A(3101)000245",
            ],
        )

    def test_purchase_in_a_dynamic_unit_splits_a_decimal_quantity(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 5, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 1234.5, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)002469",
                "(01)02000000000015(10)LOT-A(3101)002469",
                "(01)02000000000015(10)LOT-A(3101)002469",
                "(01)02000000000015(10)LOT-A(3101)002469",
                "(01)02000000000015(10)LOT-A(3101)002469",
            ],
        )

    def test_purchase_in_a_dynamic_unit_rounds_each_share_to_the_unit(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 3, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 100, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # a third of 100 kg, at the 0.01 kg rounding of the kg
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3102)003333",
                "(01)02000000000015(10)LOT-A(3102)003333",
                "(01)02000000000015(10)LOT-A(3102)003333",
            ],
        )

    def test_purchase_in_a_dynamic_box_prints_the_weight_of_one_box(self):
        # its units per box are known only when the goods are received
        uom_box = self.env["uom.uom"].create(
            {
                "name": "Box",
                "category_id": self.uom_unit.category_id.id,
                "uom_type": "bigger",
                "ratio": 1,
                "dynamic_ratio": True,
            }
        )
        product = self._create_product(
            "Product", "2000000000015", tracking="lot", weight=0.5, uom_po_id=uom_box.id
        )
        receipt = self._purchase(product, 2, uom_box)
        receipt.move_ids.move_line_ids.write({"quantity": 10, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 10 units for the 2 boxes bought is 5 units of 0.5 kg a box
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-A(3101)000025",
            ],
        )

    def test_purchase_in_a_dynamic_unit_with_a_line_of_part_of_a_unit_raises(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 3, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 3, "lot_name": "LOT-A"})
        receipt.move_ids.write(
            {
                "move_line_ids": [
                    Command.create(
                        {
                            "picking_id": receipt.id,
                            "product_id": product.id,
                            "location_id": receipt.location_id.id,
                            "location_dest_id": receipt.location_dest_id.id,
                            "quantity": 4.5,
                            "lot_name": "LOT-B",
                        }
                    )
                ]
            }
        )
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 7.5 kg for 3 pieces is 2.5 kg a piece: 3 kg is not a whole number of them
        with self.assertRaisesRegex(
            UserError, "is not a multiple of 2.5, the quantity of each unit bought"
        ):
            self._render_labels(report_action)

    def test_purchase_in_a_dynamic_unit_received_in_two_units_splits_both(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 3, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 2.5, "lot_name": "LOT-A"})
        receipt.move_ids.write(
            {
                "move_line_ids": [
                    Command.create(
                        {
                            "picking_id": receipt.id,
                            "product_id": product.id,
                            "product_uom_id": self.uom_gram.id,
                            "location_id": receipt.location_id.id,
                            "location_dest_id": receipt.location_dest_id.id,
                            "quantity": 5000,
                            "lot_name": "LOT-B",
                        }
                    )
                ]
            }
        )
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 7.5 kg for 3 pieces is 2.5 kg a piece: one in LOT-A, two in LOT-B
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-B(3101)000025",
                "(01)02000000000015(10)LOT-B(3101)000025",
            ],
        )

    def test_purchase_in_a_dynamic_unit_shares_lines_in_grams_exactly(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 4, uom_piece)
        receipt.move_ids.move_line_ids.write(
            {"product_uom_id": self.uom_gram.id, "quantity": 255, "lot_name": "LOT-A"}
        )
        receipt.move_ids.write(
            {
                "move_line_ids": [
                    Command.create(
                        {
                            "picking_id": receipt.id,
                            "product_id": product.id,
                            "product_uom_id": self.uom_gram.id,
                            "location_id": receipt.location_id.id,
                            "location_dest_id": receipt.location_dest_id.id,
                            "quantity": quantity,
                            "lot_name": lot_name,
                        }
                    )
                    for quantity, lot_name in ((255, "LOT-B"), (510, "LOT-C"))
                ]
            }
        )
        receipt.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=receipt.ids
        ).button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 1020 g for 4 pieces is 255 g a piece, and each line holds whole pieces;
        # each line rounded to the 0.01 kg of the kg would read 1030 g instead
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3102)000026",
                "(01)02000000000015(10)LOT-B(3102)000026",
                "(01)02000000000015(10)LOT-C(3102)000026",
                "(01)02000000000015(10)LOT-C(3102)000026",
            ],
        )

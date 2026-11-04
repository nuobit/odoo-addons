# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError

from .common import TestPurchaseCommon


class TestPrintPickingLabels(TestPurchaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # receipt labels print the weight received
        cls.config_gs1_128.show_weight = True

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

    def test_purchase_receipt_in_kg_prints_one_label_with_the_weight_received(self):
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        receipt = self._purchase(product, 12.5, self.uom_kg)
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # a unit that is not dynamic prints as the base module does
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3101)000125"]
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

    def test_purchase_in_a_dynamic_unit_with_a_share_below_the_kg_rounding_raises(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 300, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 1, "lot_name": "LOT-A"})
        receipt.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=receipt.ids
        ).button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 1 kg for 300 pieces is 0.0033 kg a piece, none at the 0.01 kg rounding
        with self.assertRaisesRegex(UserError, "is too small for a GS1 label"):
            self._render_labels(report_action)

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

    def _purchase_dynamic_boxes(self, quantity, weight):
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
            "Product",
            "2000000000015",
            tracking="lot",
            weight=weight,
            uom_po_id=uom_box.id,
        )
        return self._purchase(product, quantity, uom_box)

    def test_purchase_in_a_dynamic_box_weighs_its_share_to_five_decimals(self):
        receipt = self._purchase_dynamic_boxes(3, 0.4)
        receipt.move_ids.move_line_ids.write({"quantity": 35, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 35 units for the 3 boxes is 11.67 units of 0.4 kg a box, 4.66667 kg:
        # the three labels add up to the 14 kg received
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3105)466667",
                "(01)02000000000015(10)LOT-A(3105)466667",
                "(01)02000000000015(10)LOT-A(3105)466667",
            ],
        )

    def test_purchase_in_a_dynamic_box_weighs_its_share_in_pounds(self):
        # the products' weight field holds pounds
        self.env["ir.config_parameter"].sudo().set_param("product.weight_in_lbs", "1")
        receipt = self._purchase_dynamic_boxes(2, 1)
        receipt.move_ids.move_line_ids.write({"quantity": 10, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 5 units of 1 lb a box is 5 / 2.20462 = 2.26796 kg
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3105)226796",
                "(01)02000000000015(10)LOT-A(3105)226796",
            ],
        )

    def test_purchase_in_a_dynamic_box_of_a_product_without_weight_prints_none(self):
        receipt = self._purchase_dynamic_boxes(2, 0)
        receipt.move_ids.move_line_ids.write({"quantity": 10, "lot_name": "LOT-A"})
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A", "(01)02000000000015(10)LOT-A"],
        )

    def test_partial_receipt_shares_its_kilos_among_the_units_it_brings(self):
        uom_palot = self._create_dynamic_uom("Palot", 25)
        product = self._create_product(
            "Garlic",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_palot.id,
        )
        receipt = self._purchase(product, 4, uom_palot)
        # a first truck brings 2 palots of 26 kg, and the rest comes later
        receipt.move_ids.move_line_ids.write({"quantity": 52, "lot_name": "LOT-A"})
        receipt.move_ids.purchase_uom_qty = 2
        receipt.with_context(skip_backorder=True).button_validate()
        # a second truck brings the other 2, of 24 kg
        backorder = receipt.backorder_ids
        backorder.move_ids.move_line_ids.write({"quantity": 48, "lot_name": "LOT-B"})
        backorder.button_validate()
        self.assertEqual(
            self._get_label_texts(self._print_labels(receipt, self.config_gs1_128)),
            [
                "(01)02000000000015(10)LOT-A(3100)000026",
                "(01)02000000000015(10)LOT-A(3100)000026",
            ],
        )
        self.assertEqual(
            self._get_label_texts(self._print_labels(backorder, self.config_gs1_128)),
            [
                "(01)02000000000015(10)LOT-B(3100)000024",
                "(01)02000000000015(10)LOT-B(3100)000024",
            ],
        )

    def test_receipt_keeps_its_labels_once_the_order_drops_its_units(self):
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
        # all of it goes back to the vendor, and the order then buys nothing
        self._return_to_vendor(receipt, 7.5)
        receipt.move_ids.purchase_line_id.product_qty = 0
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # the receipt brought its 3 pieces all the same
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-A(3101)000025",
                "(01)02000000000015(10)LOT-A(3101)000025",
            ],
        )

    def test_receipt_without_purchase_units_received_refuses_its_labels(self):
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
        # as a receipt done before this module was installed
        receipt.move_ids.purchase_uom_qty = 0
        report_action = self._print_labels(receipt, self.config_gs1_128)
        with self.assertRaisesRegex(UserError, "has no purchase units received"):
            self._render_labels(report_action)

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
            UserError,
            r"holds 3\.0 kg of the product .+, which is not a multiple of 2\.5 kg, "
            "the quantity of each unit received",
        ):
            self._render_labels(report_action)

    def test_receipt_lines_holding_more_units_than_received_raise(self):
        uom_piece = self._create_dynamic_uom()
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_piece.id,
        )
        receipt = self._purchase(product, 3, uom_piece)
        receipt.move_ids.move_line_ids.write({"quantity": 0.01, "lot_name": "LOT-A"})
        receipt.move_ids.write(
            {
                "move_line_ids": [
                    Command.create(
                        {
                            "picking_id": receipt.id,
                            "product_id": product.id,
                            "location_id": receipt.location_id.id,
                            "location_dest_id": receipt.location_dest_id.id,
                            "quantity": 0.01,
                            "lot_name": "LOT-B",
                        }
                    )
                ]
            }
        )
        receipt.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=receipt.ids
        ).button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 0.02 kg for 3 pieces: each line of 0.01 kg rounds to 2 of them, and
        # the kg precision sees both as whole, which would print 4 labels
        with self.assertRaisesRegex(
            UserError,
            r"hold 4 units of 0\.01 kg of the product .+, but 3 purchase units "
            "were received",
        ):
            self._render_labels(report_action)

    def test_receipt_line_holding_less_than_a_unit_raises(self):
        uom_sack = self._create_dynamic_uom("Sack", 25)
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=uom_sack.id,
        )
        receipt = self._purchase(product, 1, uom_sack)
        receipt.move_ids.move_line_ids.write({"quantity": 25, "lot_name": "LOT-A"})
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
                            "quantity": 3,
                            "lot_name": "LOT-B",
                        }
                    )
                ]
            }
        )
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 3 g is no whole sack, and at the 0.01 kg precision it reads as none:
        # the line would print no label
        with self.assertRaisesRegex(
            UserError,
            r"holds 3\.0 g of the product .+, less than one of its units received",
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

    def test_return_of_a_dynamic_unit_prints_as_any_line(self):
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
        return_picking = self._return_to_vendor(receipt, 7.5)
        report_action = self._print_labels(return_picking, self.config_gs1_128)
        # a return sends kilos back: one label with the weight it sends
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A(3101)000075"],
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

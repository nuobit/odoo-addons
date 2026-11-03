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

    def test_receipt_in_dozens_prints_the_weight_of_a_dozen_on_each_label(self):
        product = self._create_product("Product", "2000000000015", weight=0.5)
        receipt = self._receive(product, 2, self.env.ref("uom.product_uom_dozen"))
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # a label per dozen received, each with 12 units of 0.5 kg
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(3100)000006", "(01)02000000000015(3100)000006"],
        )

    def test_receipt_in_millilitres_prints_the_weight_of_what_it_holds(self):
        uom_millilitre = self.env["uom.uom"].create(
            {
                "name": "Millilitre Test",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "uom_type": "smaller",
                "factor": 1000,
            }
        )
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.env.ref("uom.product_uom_litre").id,
            uom_po_id=self.env.ref("uom.product_uom_litre").id,
            weight=1,
        )
        receipt = self._receive(product, 500, uom_millilitre)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # half a litre of a product that weighs 1 kg a litre
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3101)000005"]
        )

    def test_receipt_in_milligrams_too_small_for_a_label_raises(self):
        uom_milligram = self.env["uom.uom"].create(
            {
                "name": "Milligram Test",
                "category_id": self.env.ref("uom.product_uom_categ_kgm").id,
                "uom_type": "smaller",
                "factor": 1000000,
            }
        )
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=uom_milligram.id,
            uom_po_id=uom_milligram.id,
        )
        receipt = self._receive(product, 1, uom_milligram)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        with self.assertRaisesRegex(
            UserError, "The weight 0.000001 kg is too small for a GS1 label"
        ):
            self._render_labels(report_action)

    def test_receipt_of_a_light_line_prints_its_weight_to_five_decimals(self):
        uom_millilitre = self.env["uom.uom"].create(
            {
                "name": "Millilitre Test",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "uom_type": "smaller",
                "factor": 1000,
            }
        )
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=uom_millilitre.id,
            uom_po_id=uom_millilitre.id,
            weight=0.01,
        )
        receipt = self._receive(product, 0.01, uom_millilitre)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        # 0.01 mL of a product that weighs 0.01 kg a millilitre: 0.0001 kg,
        # below the hundredths the weights are kept in
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3104)000001"]
        )

    def test_receipt_of_a_product_with_a_negative_weight_raises(self):
        product = self._create_product("Product", "2000000000015", weight=-2.5)
        receipt = self._receive(product, 1, self.uom_unit)
        report_action = self._print_labels(receipt, self.config_gs1_128)
        with self.assertRaisesRegex(UserError, "The weight of Product is negative"):
            self._render_labels(report_action)

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

    def test_receipt_prints_in_internal_reference_order(self):
        product_b = self._create_product(
            "Product B", "2000000000022", default_code="REF-B"
        )
        product_a = self._create_product(
            "Product A", "2000000000015", default_code="REF-A"
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
                            "product_uom_qty": 1,
                            "product_uom": self.uom_unit.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        }
                    )
                    # received in the reverse order of their references
                    for product in (product_b, product_a)
                ],
            }
        )
        receipt.action_confirm()
        receipt.button_validate()
        report_action = self._print_labels(receipt, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015", "(01)02000000000022"],
        )

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

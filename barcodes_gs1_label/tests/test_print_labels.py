# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, new_test_user

from .common import TestCommon


class TestPrintLabels(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config_ean13 = cls.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "EAN13",
                "format_id": cls.label_format.id,
                "barcode_type": "ean13",
            }
        )
        cls.config_ean13_code128 = cls.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "EAN13 + Code128",
                "format_id": cls.label_format.id,
                "barcode_type": "ean13-code128",
            }
        )

    def test_product_with_stock_prints_one_label_per_unit(self):
        product = self._create_product("Product", "2000000000015")
        self._set_stock(product, self.stock_location, 3)
        report_action = self._print_labels(product, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015", "(01)02000000000015", "(01)02000000000015"],
        )

    def test_product_without_stock_option_prints_one_label(self):
        product = self._create_product("Product", "2000000000015")
        self._set_stock(product, self.stock_location, 3)
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False
        )
        self.assertEqual(self._get_label_texts(report_action), ["(01)02000000000015"])

    def test_product_print_wizard_proposes_the_locations_with_stock(self):
        product = self._create_product("Product", "2000000000015")
        shelf = self.env["stock.location"].create(
            {"name": "Shelf", "location_id": self.stock_location.id}
        )
        self.env["stock.location"].create(
            {"name": "Empty shelf", "location_id": self.stock_location.id}
        )
        self._set_stock(product, self.stock_location, 2)
        self._set_stock(product, shelf, 1)
        action = product.with_user(self.user).print_gs1_barcode_wizard()
        wizard_form = Form(
            self.env[action["res_model"]]
            .with_user(self.user)
            .with_context(active_model="product.product", active_ids=product.ids)
        )
        wizard_form.label_config_id = self.config_gs1_128
        wizard = wizard_form.save()
        self.assertEqual(wizard.stock_location_ids, self.stock_location + shelf)

    def test_location_removed_in_the_print_wizard_is_not_printed(self):
        product = self._create_product("Product", "2000000000015")
        shelf = self.env["stock.location"].create(
            {"name": "Shelf", "location_id": self.stock_location.id}
        )
        self._set_stock(product, self.stock_location, 2)
        self._set_stock(product, shelf, 1)
        action = product.with_user(self.user).print_gs1_barcode_wizard()
        wizard_form = Form(
            self.env[action["res_model"]]
            .with_user(self.user)
            .with_context(active_model="product.product", active_ids=product.ids)
        )
        wizard_form.label_config_id = self.config_gs1_128
        wizard_form.stock_location_ids.remove(id=shelf.id)
        wizard = wizard_form.save()
        # the print button runs in a request of its own, with an empty cache
        wizard.invalidate_recordset()
        self.assertEqual(
            self._get_label_texts(wizard.print_product_barcodes()),
            ["(01)02000000000015", "(01)02000000000015"],
        )

    def test_print_wizards_computed_together_propose_each_their_locations(self):
        # a company of its own, whose internal locations are those of the test
        company = self.env["res.company"].create({"name": "Labels company"})
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)]
        )
        user = new_test_user(
            self.env,
            login="gs1_label_locations_test",
            groups="stock.group_stock_manager",
            company_id=company.id,
        )
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "GS1-128",
                "format_id": self.label_format.id,
                "barcode_type": "gs1-128",
                "company_id": company.id,
            }
        )
        product = self._create_product("Product", "2000000000015")
        shelf = self.env["stock.location"].create(
            {
                "name": "Shelf",
                "location_id": warehouse.lot_stock_id.id,
                "company_id": company.id,
            }
        )
        self._set_stock(product, shelf, 1)
        wizards = (
            self.env["barcodes.gs1.label.options.wizard"]
            .with_user(user)
            .with_context(active_model="product.product", active_ids=product.ids)
            .create(
                [
                    {"label_config_id": config.id, "with_stock": True},
                    {"label_config_id": config.id, "with_stock": False},
                ]
            )
        )
        self.assertEqual(wizards[0].stock_location_ids, shelf)
        self.assertEqual(wizards[1].stock_location_ids, warehouse.lot_stock_id + shelf)

    def test_print_with_stock_but_no_location_is_refused_on_save(self):
        # no stock anywhere, so no location to propose
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            ValidationError,
            'Choose the locations whose stock is printed, or untick "With stock only"',
        ):
            self.env["barcodes.gs1.label.options.wizard"].with_context(
                active_model="product.product", active_ids=product.ids
            ).create({"label_config_id": self.config_gs1_128.id, "with_stock": True})

    def test_print_wizards_keep_their_own_records_to_propose_locations(self):
        product_1 = self._create_product("Product 1", "2000000000015")
        product_2 = self._create_product("Product 2", "2000000000022")
        shelf_1 = self.env["stock.location"].create(
            {"name": "Shelf 1", "location_id": self.stock_location.id}
        )
        shelf_2 = self.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": self.stock_location.id}
        )
        self._set_stock(product_1, shelf_1, 1)
        self._set_stock(product_2, shelf_2, 1)
        wizard_1 = (
            self.env["barcodes.gs1.label.options.wizard"]
            .with_context(active_model="product.product", active_ids=product_1.ids)
            .create({"label_config_id": self.config_gs1_128.id, "with_stock": False})
        )
        wizard_2 = (
            self.env["barcodes.gs1.label.options.wizard"]
            .with_context(active_model="product.product", active_ids=product_2.ids)
            .create({"label_config_id": self.config_gs1_128.id, "with_stock": False})
        )
        # switched on together, away from the action that opened each of them
        (wizard_1 + wizard_2).write({"with_stock": True})
        self.assertEqual(wizard_1.stock_location_ids, shelf_1)
        self.assertEqual(wizard_2.stock_location_ids, shelf_2)

    def test_products_print_in_internal_reference_order(self):
        product_b = self._create_product(
            "Product B", "2000000000022", default_code="REF-B"
        )
        product_a = self._create_product(
            "Product A", "2000000000015", default_code="REF-A"
        )
        report_action = self._print_labels(
            product_b + product_a, self.config_gs1_128, with_stock=False
        )
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015", "(01)02000000000022"],
        )

    def test_product_with_lots_prints_one_label_per_unit_of_each_lot(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        lot_b = self._create_lot(product, "LOT-B")
        lot_a = self._create_lot(product, "LOT-A")
        self._set_stock(product, self.stock_location, 2, lot=lot_b)
        self._set_stock(product, self.stock_location, 1, lot=lot_a)
        report_action = self._print_labels(product, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015(10)LOT-A",
                "(01)02000000000015(10)LOT-B",
                "(01)02000000000015(10)LOT-B",
            ],
        )

    def test_product_with_lots_without_stock_option_prints_one_label_per_lot(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        self._create_lot(product, "LOT-B")
        self._create_lot(product, "LOT-A")
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False
        )
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A", "(01)02000000000015(10)LOT-B"],
        )

    def test_product_with_serials_prints_the_lot_reference_and_the_serial(self):
        product = self._create_product("Product", "2000000000015", tracking="serial")
        serial = self._create_lot(product, "SN-001", ref="LOT-REF")
        self._set_stock(product, self.stock_location, 1, lot=serial)
        report_action = self._print_labels(product, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-REF(21)SN-001"],
        )

    def test_gs1_barcode_closes_a_variable_length_value_followed_by_another(self):
        product = self._create_product("Product", "2000000000015", tracking="serial")
        serial = self._create_lot(product, "SN-001", ref="LOT-REF")
        self._set_stock(product, self.stock_location, 1, lot=serial)
        report_action = self._print_labels(product, self.config_gs1_128)
        # FNC1 (%C3%B1) starts the code and ends the lot, not the last value
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-barcode-img')]/img/@src"
            ),
            [
                "/report/barcode/?barcode_type=gs1-128"
                "&value=%C3%B1010200000000001510LOT-REF%C3%B121SN-001&height=100"
            ],
        )

    def test_gs1_datamatrix_closes_a_variable_length_value_followed_by_another(self):
        config = self._create_config("gs1-datamatrix", 70, 37)
        product = self._create_product("Product", "2000000000015", tracking="serial")
        serial = self._create_lot(product, "SN-001", ref="LOT-REF")
        self._set_stock(product, self.stock_location, 1, lot=serial)
        report_action = self._print_labels(product, config)
        # FNC1 (%C3%A7) starts the code and ends the lot, not the last value
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-barcode-img')]/img/@src"
            ),
            [
                "/report/barcode/?barcode_type=gs1-datamatrix"
                "&value=%C3%A7010200000000001510LOT-REF%C3%A721SN-001&height=100"
            ],
        )

    def test_label_copies_repeat_each_product_and_lot_label(self):
        product = self._create_product("Product", "2000000000015", default_code="REF-A")
        product_with_lots = self._create_product(
            "Product with lots", "2000000000022", default_code="REF-B", tracking="lot"
        )
        self._create_lot(product_with_lots, "LOT-A")
        report_action = self._print_labels(
            product + product_with_lots,
            self.config_gs1_128,
            with_stock=False,
            label_copies=2,
        )
        self.assertEqual(
            self._get_label_texts(report_action),
            [
                "(01)02000000000015",
                "(01)02000000000015",
                "(01)02000000000022(10)LOT-A",
                "(01)02000000000022(10)LOT-A",
            ],
        )

    def test_label_copies_do_not_repeat_serial_labels(self):
        product = self._create_product("Product", "2000000000015", tracking="serial")
        self._create_lot(product, "SN-001")
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, label_copies=2
        )
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(21)SN-001"]
        )

    def test_product_in_kg_prints_the_weight_of_the_wizard(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, weight=10
        )
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3100)000010"]
        )

    def test_product_in_units_prints_the_weight_of_the_wizard(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, weight=10
        )
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3100)000010"]
        )

    def test_weight_of_more_than_six_digits_raises(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, weight=1234.567
        )
        with self.assertRaisesRegex(
            UserError, "The weight 1234.567 kg has more digits than the 6"
        ):
            self._render_labels(report_action)

    def test_weight_with_five_decimals_prints_them(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, weight=0.00005
        )
        self.assertEqual(
            self._get_label_texts(report_action), ["(01)02000000000015(3105)000005"]
        )

    def test_weight_with_six_decimals_raises(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product(
            "Product",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False, weight=0.000123
        )
        with self.assertRaisesRegex(
            UserError, "The weight 0.000123 kg has more decimals than the 5"
        ):
            self._render_labels(report_action)

    def test_weight_with_seven_decimals_raises(self):
        # a weight with more decimals than the precisions of Odoo give, so
        # that only the encoding can see them
        with self.assertRaisesRegex(
            UserError, "The weight 1.0000001 kg has more decimals than the 5"
        ):
            self.env["report.barcodes_gs1_label.report_gs1_barcode"]._get_weight_ai31(
                1.0000001
            )

    def test_quant_print_wizard_saves_without_locations(self):
        product = self._create_product("Product", "2000000000015")
        self._set_stock(product, self.stock_location, 2)
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        wizard = (
            self.env["barcodes.gs1.label.options.wizard"]
            .with_user(self.user)
            .with_context(active_model="stock.quant", active_ids=quant.ids)
            .create({"label_config_id": self.config_gs1_128.id})
        )
        # quants print themselves: their form shows no stock options
        wizard.stock_location_ids = False
        self.assertFalse(wizard.stock_location_ids)

    def test_lot_print_wizard_proposes_the_locations_with_stock(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        lot = self._create_lot(product, "LOT-A")
        other_lot = self._create_lot(product, "LOT-B")
        shelf = self.env["stock.location"].create(
            {"name": "Shelf", "location_id": self.stock_location.id}
        )
        other_shelf = self.env["stock.location"].create(
            {"name": "Other shelf", "location_id": self.stock_location.id}
        )
        self.env["stock.location"].create(
            {"name": "Empty shelf", "location_id": self.stock_location.id}
        )
        self._set_stock(product, self.stock_location, 2, lot=lot)
        self._set_stock(product, shelf, 1, lot=lot)
        # the same product, but another lot
        self._set_stock(product, other_shelf, 4, lot=other_lot)
        action = lot.with_user(self.user).print_gs1_barcode_wizard()
        wizard_form = Form(
            self.env[action["res_model"]]
            .with_user(self.user)
            .with_context(active_model="stock.lot", active_ids=lot.ids)
        )
        wizard_form.label_config_id = self.config_gs1_128
        wizard = wizard_form.save()
        self.assertEqual(wizard.stock_location_ids, self.stock_location + shelf)

    def test_lot_with_stock_prints_one_label_per_unit(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        lot_a = self._create_lot(product, "LOT-A")
        lot_b = self._create_lot(product, "LOT-B")
        self._set_stock(product, self.stock_location, 2, lot=lot_a)
        self._set_stock(product, self.stock_location, 1, lot=lot_b)
        report_action = self._print_labels(lot_a, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A", "(01)02000000000015(10)LOT-A"],
        )

    def test_lot_in_kg_prints_the_weight_of_the_wizard(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product(
            "Product",
            "2000000000015",
            tracking="lot",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        lot = self._create_lot(product, "LOT-A")
        report_action = self._print_labels(
            lot, self.config_gs1_128, with_stock=False, weight=0.75
        )
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A(3102)000075"],
        )

    def test_lot_in_units_prints_the_weight_of_the_wizard(self):
        self.config_gs1_128.show_weight = True
        product = self._create_product("Product", "2000000000015", tracking="lot")
        lot = self._create_lot(product, "LOT-A")
        report_action = self._print_labels(
            lot, self.config_gs1_128, with_stock=False, weight=0.75
        )
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015(10)LOT-A(3102)000075"],
        )

    def test_print_wizard_hides_the_weight_without_the_option(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            AssertionError, "can't write on invisible field 'weight'"
        ):
            self._print_labels(
                product, self.config_gs1_128, with_stock=False, weight=10
            )

    def test_print_wizard_hides_the_weight_on_ean13_labels(self):
        self.config_ean13.show_weight = True
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            AssertionError, "can't write on invisible field 'weight'"
        ):
            self._print_labels(product, self.config_ean13, with_stock=False, weight=10)

    def test_lot_name_longer_than_twenty_characters_raises(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        lot = self._create_lot(product, "LOT-0123456789ABCDEFG")
        report_action = self._print_labels(lot, self.config_gs1_128, with_stock=False)
        with self.assertRaisesRegex(
            ValidationError,
            r"The value 'LOT-0123456789ABCDEFG' of GS1 AI 10 is too long \(max 20",
        ):
            self._render_labels(report_action)

    def test_quant_prints_one_label_per_unit(self):
        product = self._create_product("Product", "2000000000015")
        self._set_stock(product, self.stock_location, 2)
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        report_action = self._print_labels(quant, self.config_gs1_128)
        self.assertEqual(
            self._get_label_texts(report_action),
            ["(01)02000000000015", "(01)02000000000015"],
        )

    def test_ean13_code128_prints_the_product_and_the_lot_barcodes(self):
        product = self._create_product("Product", "2000000000015", tracking="lot")
        self._create_lot(product, "LOT-A")
        report_action = self._print_labels(
            product, self.config_ean13_code128, with_stock=False
        )
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-barcode-img')]/img/@src"
            ),
            [
                "/report/barcode/?barcode_type=EAN13&quiet=0&value=2000000000015"
                "&height=80",
                "/report/barcode/?barcode_type=Code128&quiet=0&value=LOT-A&height=80",
            ],
        )

    def test_ean13_prints_the_product_barcode(self):
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(product, self.config_ean13, with_stock=False)
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-barcode-img')]/img/@src"
            ),
            [
                "/report/barcode/?barcode_type=EAN13&quiet=0&value=2000000000015"
                "&height=80"
            ],
        )

    def _get_prices(self, report_action):
        return [
            "".join(price.text_content().split())
            for price in self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-price')]"
            )
        ]

    def test_ean13_label_without_the_currency_option_prints_the_bare_price(self):
        self.config_ean13.show_price = True
        product = self._create_product("Product", "2000000000015", list_price=12.5)
        report_action = self._print_labels(product, self.config_ean13, with_stock=False)
        self.assertEqual(self._get_prices(report_action), ["12.50"])

    def test_ean13_code128_label_without_the_option_prints_the_bare_price(self):
        self.config_ean13_code128.show_price = True
        product = self._create_product("Product", "2000000000015", list_price=12.5)
        report_action = self._print_labels(
            product, self.config_ean13_code128, with_stock=False
        )
        self.assertEqual(self._get_prices(report_action), ["12.50"])

    def test_ean13_label_with_the_currency_option_prints_the_currency(self):
        self.config_ean13.write({"show_price": True, "show_price_currency": True})
        product = self._create_product("Product", "2000000000015", list_price=12.5)
        # the label prints the product's currency, given here a known symbol
        product.currency_id.write({"symbol": "¤", "position": "after"})
        report_action = self._print_labels(product, self.config_ean13, with_stock=False)
        self.assertEqual(self._get_prices(report_action), ["12.50¤"])

    def test_gs1_label_prints_the_currency_without_the_option(self):
        self.config_gs1_128.show_price = True
        product = self._create_product("Product", "2000000000015", list_price=12.5)
        # the label prints the product's currency, given here a known symbol
        product.currency_id.write({"symbol": "¤", "position": "after"})
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False
        )
        self.assertEqual(self._get_prices(report_action), ["12.50¤"])

    def test_labels_report_without_the_print_wizard_raises(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            UserError,
            "The labels are printed with the options of the print wizard: "
            "open it from the records and choose the label options.",
        ):
            self.env["ir.actions.report"].with_user(self.user)._render_qweb_pdf(
                "barcodes_gs1_label.action_report_product_gs1_barcodes", product.ids
            )

    def test_labels_report_with_options_not_from_the_print_wizard_raises(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            UserError, "The labels are printed with the options of the print wizard"
        ):
            self.env["ir.actions.report"].with_user(self.user)._render_qweb_pdf(
                "barcodes_gs1_label.action_report_product_gs1_barcodes",
                product.ids,
                data={"barcode_type": "gs1-128"},
            )

    def test_gs1_128_label_with_nothing_to_encode_shows_the_product(self):
        product = self._create_product("Product C", False, default_code="REF-C")
        report_action = self._print_labels(
            product, self.config_gs1_128, with_stock=False
        )
        cells = self._render_labels(report_action).xpath("//div[hasclass('bgp-cell')]")
        label = cells[0]
        self.assertEqual(
            [
                " ".join(label.xpath(f"string(.//div[hasclass('{css}')])").split())
                for css in ("bgp-sku", "bgp-description")
            ],
            ["REF-C", "Product C"],
        )
        self.assertFalse(label.xpath(".//div[hasclass('bgp-barcode')]"))

    def test_gs1_datamatrix_label_with_nothing_to_encode_shows_the_product(self):
        product = self._create_product("Product C", False, default_code="REF-C")
        config = self._create_config("gs1-datamatrix", 70, 37)
        report_action = self._print_labels(product, config, with_stock=False)
        cells = self._render_labels(report_action).xpath("//div[hasclass('bgp-cell')]")
        label = cells[0]
        self.assertEqual(
            [
                " ".join(label.xpath(f"string(.//div[hasclass('{css}')])").split())
                for css in ("bgp-sku", "bgp-description")
            ],
            ["REF-C", "Product C"],
        )
        self.assertFalse(label.xpath(".//div[hasclass('bgp-barcode')]"))

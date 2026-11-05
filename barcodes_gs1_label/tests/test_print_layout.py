# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError, ValidationError

from .common import TestCommon


class TestPrintLayout(TestCommon):
    def test_print_layout_shares_the_sheet_pixels_among_the_labels(self):
        config = self._create_config("gs1-128", 69, 37)
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(product, config, with_stock=False)
        # The A4 sheet of 254 dpi gives 10 px per mm, 12.5 px with the default
        # correction of 1.25: 3 columns of 862.5 px and 8 rows of 462.5 px
        layout = report_action["data"]["layout"]
        self.assertEqual(layout["label_widths"], [863, 862, 862])
        self.assertEqual(
            layout["label_heights"], [463, 463, 463, 463, 462, 462, 462, 462]
        )
        self.assertEqual(layout["container_width"], 2587)
        self.assertEqual(layout["container_top"], 6)

    def test_print_from_the_last_cell_continues_on_a_new_page(self):
        config = self._create_config("gs1-128", 70, 37)
        product = self._create_product("Product", "2000000000015")
        self._set_stock(product, self.stock_location, 2)
        report_action = self._print_labels(product, config, start_row=8, start_col=3)
        self.assertEqual(
            self._get_pages(report_action),
            [
                [""] * 23 + ["(01)02000000000015"],
                ["(01)02000000000015", "", ""],
            ],
        )

    def test_print_start_column_after_the_last_column_raises(self):
        config = self._create_config("gs1-128", 70, 37)
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            UserError, "Start column should be between 1 and 3"
        ):
            self._print_labels(product, config, with_stock=False, start_col=4)

    def test_print_start_column_before_the_first_column_raises(self):
        config = self._create_config("gs1-128", 70, 37)
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            UserError, "Start column should be between 1 and 3"
        ):
            self._print_labels(product, config, with_stock=False, start_col=0)

    def test_print_start_row_after_the_last_row_raises(self):
        config = self._create_config("gs1-128", 70, 37)
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(UserError, "Start row should be between 1 and 8"):
            self._print_labels(product, config, with_stock=False, start_row=9)

    def test_print_start_row_before_the_first_row_raises(self):
        config = self._create_config("gs1-128", 70, 37)
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(UserError, "Start row should be between 1 and 8"):
            self._print_labels(product, config, with_stock=False, start_row=0)

    def test_print_on_paper_that_lost_its_size_raises(self):
        paperformat = self.env["report.paperformat"].create(
            {"name": "Labels paper", "format": "A4", "orientation": "Portrait"}
        )
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "70 x 37 mm",
                "paperformat_id": paperformat.id,
                "label_width": 70,
                "label_height": 37,
            }
        )
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Shelf labels",
                "format_id": label_format.id,
                "barcode_type": "gs1-128",
            }
        )
        product = self._create_product("Product", "2000000000015")
        paperformat.format = False
        with self.assertRaisesRegex(
            ValidationError, "The paper format 'Labels paper' has no paper size"
        ):
            self._print_labels(product, config, with_stock=False)

    def test_print_on_custom_paper_that_lost_its_size_raises(self):
        paperformat = self.env["report.paperformat"].create(
            {
                "name": "Custom labels paper",
                "format": "custom",
                "page_width": 210,
                "page_height": 297,
                "orientation": "Portrait",
            }
        )
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "70 x 37 mm",
                "paperformat_id": paperformat.id,
                "label_width": 70,
                "label_height": 37,
            }
        )
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Shelf labels",
                "format_id": label_format.id,
                "barcode_type": "gs1-128",
            }
        )
        product = self._create_product("Product", "2000000000015")
        paperformat.page_width = 0
        with self.assertRaisesRegex(
            ValidationError,
            "The paper format 'Custom labels paper' is custom and has no width or "
            "height",
        ):
            self._print_labels(product, config, with_stock=False)

    def test_print_without_copies_raises(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            UserError, "The number of copies must be greater than 0"
        ):
            self._print_labels(
                product, self.config_gs1_128, with_stock=False, label_copies=0
            )

    def test_datamatrix_on_a_landscape_label_uses_the_landscape_layout(self):
        config = self._create_config("gs1-datamatrix", 70, 37)
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(product, config, with_stock=False)
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-cell')]/div/@class"
            ),
            ["bgp-gs1-datamatrix-landscape"],
        )

    def test_datamatrix_on_a_portrait_label_uses_the_portrait_layout(self):
        config = self._create_config("gs1-datamatrix", 37, 70)
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(product, config, with_stock=False)
        self.assertEqual(
            self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-cell')]/div/@class"
            ),
            ["bgp-gs1-datamatrix"],
        )

    def test_borders_print_with_the_chosen_color(self):
        product = self._create_product("Product", "2000000000015")
        report_action = self._print_labels(
            product,
            self.config_gs1_128,
            with_stock=False,
            show_borders=True,
            border_color="#000000",
        )
        cells = self._render_labels(report_action).xpath("//div[hasclass('bgp-cell')]")
        self.assertIn("border:1px solid #000000;", cells[0].get("style"))

    def test_borders_without_a_color_raises(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(AssertionError, "border_color is a required field"):
            self._print_labels(
                product,
                self.config_gs1_128,
                with_stock=False,
                show_borders=True,
                border_color=False,
            )

    def test_borders_without_a_color_are_refused_on_save(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(ValidationError, "color of the borders"):
            self.env["barcodes.gs1.label.options.wizard"].with_context(
                active_model="product.product", active_ids=product.ids
            ).create(
                {
                    "label_config_id": self.config_gs1_128.id,
                    "with_stock": False,
                    "show_borders": True,
                    "border_color": False,
                }
            )

    def test_border_color_is_hidden_without_borders(self):
        product = self._create_product("Product", "2000000000015")
        with self.assertRaisesRegex(
            AssertionError, "can't write on invisible field 'border_color'"
        ):
            self._print_labels(
                product, self.config_gs1_128, with_stock=False, border_color="#000000"
            )

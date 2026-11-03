# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user
from odoo.tools.safe_eval import safe_eval
from odoo.tools.view_validation import get_expression_field_names

from .common import TestCommon


class TestLabelConfig(TestCommon):
    def test_second_default_configuration_of_a_company_raises(self):
        company = self.env["res.company"].create({"name": "Labels company"})
        self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Default",
                "format_id": self.label_format.id,
                "barcode_type": "gs1-128",
                "company_id": company.id,
                "default": True,
            }
        )
        with self.assertRaisesRegex(
            UserError, "Only one label configuration can be set as default"
        ):
            self.env["barcodes.gs1.label.options.config"].create(
                {
                    "name": "Second default",
                    "format_id": self.label_format.id,
                    "barcode_type": "gs1-datamatrix",
                    "company_id": company.id,
                    "default": True,
                }
            )

    def test_default_configuration_in_each_company_passes(self):
        company_1 = self.env["res.company"].create({"name": "Labels company 1"})
        company_2 = self.env["res.company"].create({"name": "Labels company 2"})
        config_1 = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Default",
                "format_id": self.label_format.id,
                "barcode_type": "gs1-128",
                "company_id": company_1.id,
                "default": True,
            }
        )
        config_2 = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Default",
                "format_id": self.label_format.id,
                "barcode_type": "gs1-128",
                "company_id": company_2.id,
                "default": True,
            }
        )
        # each company keeps its own default
        self.assertEqual(
            (config_1 | config_2).filtered("default").company_id,
            company_1 | company_2,
        )

    def test_print_wizard_proposes_the_default_configuration_of_the_company(self):
        company = self.env["res.company"].create({"name": "Labels company"})
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Default",
                "format_id": self.label_format.id,
                "barcode_type": "gs1-128",
                "company_id": company.id,
                "default": True,
            }
        )
        user = new_test_user(
            self.env,
            login="gs1_label_company_manager_test",
            groups="stock.group_stock_manager",
            company_id=company.id,
        )
        product = self._create_product("Product", "2000000000015")
        action = product.with_user(user).print_gs1_barcode_wizard()
        wizard_form = Form(
            self.env[action["res_model"]]
            .with_user(user)
            .with_context(active_model="product.product", active_ids=product.ids)
        )
        self.assertEqual(wizard_form.label_config_id, config)

    def test_configuration_name_shows_its_format_and_barcode_type(self):
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Shelf labels",
                "format_id": self.label_format.id,
                "barcode_type": "ean13-code128",
            }
        )
        self.assertEqual(
            config.display_name,
            "Shelf labels - A4 portrait labels (70 x 37 mm) [24] - EAN13 + Code128",
        )

    def test_configuration_name_follows_its_paper(self):
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Shelf labels",
                "format_id": self.label_format.id,
                "barcode_type": "ean13-code128",
            }
        )
        self.assertEqual(
            config.display_name,
            "Shelf labels - A4 portrait labels (70 x 37 mm) [24] - EAN13 + Code128",
        )
        self.label_format.paperformat_id.name = "A4 shelf labels"
        self.assertEqual(
            config.display_name,
            "Shelf labels - A4 shelf labels (70 x 37 mm) [24] - EAN13 + Code128",
        )

    def test_configuration_name_follows_its_barcode_type(self):
        config = self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Shelf labels",
                "format_id": self.label_format.id,
                "barcode_type": "ean13-code128",
            }
        )
        self.assertEqual(
            config.display_name,
            "Shelf labels - A4 portrait labels (70 x 37 mm) [24] - EAN13 + Code128",
        )
        config.barcode_type = "ean13"
        self.assertEqual(
            config.display_name,
            "Shelf labels - A4 portrait labels (70 x 37 mm) [24] - EAN13",
        )

    def test_configuration_name_on_paper_that_lost_its_size_fits_no_label(self):
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
                "barcode_type": "ean13",
            }
        )
        # read before the paper changes, so that the change must reach it
        self.assertEqual(
            config.display_name, "Shelf labels - Labels paper (70 x 37 mm) [24] - EAN13"
        )
        paperformat.format = False
        self.assertEqual(
            config.display_name, "Shelf labels - Labels paper (70 x 37 mm) [0] - EAN13"
        )

    def test_configuration_name_on_paper_that_lost_its_orientation_fits_no_label(self):
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
                "barcode_type": "ean13",
            }
        )
        # read before the paper changes, so that the change must reach it
        self.assertEqual(
            config.display_name, "Shelf labels - Labels paper (70 x 37 mm) [24] - EAN13"
        )
        paperformat.orientation = False
        self.assertEqual(
            config.display_name, "Shelf labels - Labels paper (70 x 37 mm) [0] - EAN13"
        )

    def test_new_configuration_name_shows_only_what_is_set(self):
        config = self.env["barcodes.gs1.label.options.config"].new(
            {"name": "Shelf labels"}
        )
        self.assertEqual(config.display_name, "Shelf labels")

    def _new_config_form(self, barcode_type, show_price):
        config_form = Form(self.env["barcodes.gs1.label.options.config"])
        config_form.name = "Labels"
        config_form.format_id = self.label_format
        config_form.barcode_type = barcode_type
        config_form.show_price = show_price
        return config_form

    def test_configuration_offers_the_currency_option_on_priced_ean13_labels(self):
        config_form = self._new_config_form("ean13", show_price=True)
        config_form.show_price_currency = True
        self.assertTrue(config_form.save().show_price_currency)

    def test_configuration_hides_the_currency_option_without_the_price(self):
        config_form = self._new_config_form("ean13", show_price=False)
        with self.assertRaisesRegex(
            AssertionError, "can't write on invisible field 'show_price_currency'"
        ):
            config_form.show_price_currency = True

    def test_configuration_hides_the_currency_option_on_gs1_labels(self):
        config_form = self._new_config_form("gs1-128", show_price=True)
        with self.assertRaisesRegex(
            AssertionError, "can't write on invisible field 'show_price_currency'"
        ):
            config_form.show_price_currency = True

    def _create_row(self, barcode_type, show_price):
        return self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "Labels",
                "format_id": self.label_format.id,
                "barcode_type": barcode_type,
                "show_price": show_price,
            }
        )

    def _list_shows(self, row, field_name):
        # a list has no Form helper: evaluate the column's invisible expression
        # on the row's values, as the web client does for each row
        arch = row.get_views([(False, "list")])["views"]["list"]["arch"]
        (column,) = etree.fromstring(arch).xpath(f"//field[@name='{field_name}']")
        invisible = column.get("invisible", "False")
        values = {name: row[name] for name in get_expression_field_names(invisible)}
        return not safe_eval(invisible, values)

    def test_configuration_list_shows_the_currency_option_on_priced_ean13_rows(self):
        row = self._create_row("ean13", show_price=True)
        self.assertTrue(self._list_shows(row, "show_price_currency"))

    def test_configuration_list_hides_the_currency_option_on_unpriced_rows(self):
        row = self._create_row("ean13", show_price=False)
        self.assertFalse(self._list_shows(row, "show_price_currency"))

    def test_configuration_list_hides_the_currency_option_on_gs1_rows(self):
        row = self._create_row("gs1-128", show_price=True)
        self.assertFalse(self._list_shows(row, "show_price_currency"))

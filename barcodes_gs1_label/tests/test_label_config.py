# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user

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

    def test_new_configuration_name_shows_only_what_is_set(self):
        config = self.env["barcodes.gs1.label.options.config"].new(
            {"name": "Shelf labels"}
        )
        self.assertEqual(config.display_name, "Shelf labels")

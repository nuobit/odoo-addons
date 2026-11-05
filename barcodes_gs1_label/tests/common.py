# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import lxml.html

from odoo.tests import Form, common, new_test_user


class TestCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="gs1_label_manager_test",
            groups="stock.group_stock_manager",
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.paperformat_a4_portrait = cls.env["report.paperformat"].create(
            {
                "name": "A4 portrait labels",
                "format": "A4",
                "orientation": "Portrait",
                "dpi": 254,
            }
        )
        cls.label_format = cls.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "70 x 37 mm",
                "paperformat_id": cls.paperformat_a4_portrait.id,
                "label_width": 70,
                "label_height": 37,
            }
        )
        cls.config_gs1_128 = cls.env["barcodes.gs1.label.options.config"].create(
            {
                "name": "GS1-128",
                "format_id": cls.label_format.id,
                "barcode_type": "gs1-128",
            }
        )

    def _create_config(self, barcode_type, label_width, label_height):
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": f"{label_width:g} x {label_height:g} mm",
                "paperformat_id": self.paperformat_a4_portrait.id,
                "label_width": label_width,
                "label_height": label_height,
            }
        )
        return self.env["barcodes.gs1.label.options.config"].create(
            {
                "name": f"{barcode_type} {label_format.name}",
                "format_id": label_format.id,
                "barcode_type": barcode_type,
            }
        )

    def _create_product(self, name, barcode, **values):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
                "barcode": barcode,
                **values,
            }
        )

    def _create_lot(self, product, name, **values):
        return self.env["stock.lot"].create(
            {
                "name": name,
                "product_id": product.id,
                **values,
            }
        )

    def _set_stock(self, product, location, quantity, lot=None):
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "lot_id": lot.id if lot is not None else False,
                "inventory_quantity": quantity,
            }
        ).action_apply_inventory()

    def _print_labels(self, records, label_config, **wizard_values):
        action = records.with_user(self.user).print_gs1_barcode_wizard()
        wizard_form = Form(
            self.env[action["res_model"]]
            .with_user(self.user)
            .with_context(active_model=records._name, active_ids=records.ids)
        )
        wizard_form.label_config_id = label_config
        for field_name, value in wizard_values.items():
            setattr(wizard_form, field_name, value)
        return wizard_form.save().print_product_barcodes()

    def _render_labels(self, report_action):
        html, _report_type = (
            self.env["ir.actions.report"]
            .with_user(self.user)
            .with_context(**report_action["context"])
            ._render_qweb_pdf(report_action["report_name"], data=report_action["data"])
        )
        return lxml.html.fromstring(html)

    def _get_label_texts(self, report_action):
        return [
            "".join(text.text_content().split())
            for text in self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-barcode-text')]"
            )
        ]

    def _get_pages(self, report_action):
        return [
            [
                "".join(
                    cell.xpath("string(.//div[hasclass('bgp-barcode-text')])").split()
                )
                for cell in page.xpath(".//div[hasclass('bgp-cell')]")
            ]
            for page in self._render_labels(report_action).xpath(
                "//div[hasclass('bgp-page')]"
            )
        ]

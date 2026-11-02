# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests import Form

from .common import TestCommon


class TestLabelFormat(TestCommon):
    def test_format_fits_the_labels_in_the_sheet(self):
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "70 x 37 mm",
                "paperformat_id": self.paperformat_a4_portrait.id,
                "label_width": 70,
                "label_height": 37,
            }
        )
        self.assertEqual(label_format.sheet_width, 210)
        self.assertEqual(label_format.sheet_height, 297)
        self.assertEqual(label_format.page_cols_max, 3)
        self.assertEqual(label_format.page_rows_max, 8)
        self.assertEqual(label_format.page_max_labels, 24)

    def test_format_on_landscape_paper_turns_the_sheet(self):
        paperformat = self.env["report.paperformat"].create(
            {
                "name": "A4 landscape labels",
                "format": "A4",
                "orientation": "Landscape",
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
        self.assertEqual(label_format.sheet_width, 297)
        self.assertEqual(label_format.sheet_height, 210)
        self.assertEqual(label_format.page_cols_max, 4)
        self.assertEqual(label_format.page_rows_max, 5)
        self.assertEqual(label_format.page_max_labels, 20)

    def test_format_with_a_label_wider_than_the_sheet_fits_no_label(self):
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "250 x 37 mm",
                "paperformat_id": self.paperformat_a4_portrait.id,
                "label_width": 250,
                "label_height": 37,
            }
        )
        self.assertEqual(label_format.page_cols_max, 0)
        self.assertEqual(label_format.page_rows_max, 0)
        self.assertEqual(label_format.page_max_labels, 0)

    def test_format_with_a_label_taller_than_the_sheet_fits_no_label(self):
        label_format = self.env["barcodes.gs1.label.options.format"].create(
            {
                "name": "70 x 300 mm",
                "paperformat_id": self.paperformat_a4_portrait.id,
                "label_width": 70,
                "label_height": 300,
            }
        )
        self.assertEqual(label_format.page_cols_max, 0)
        self.assertEqual(label_format.page_rows_max, 0)
        self.assertEqual(label_format.page_max_labels, 0)

    def test_format_form_counts_the_labels_once_both_sizes_are_set(self):
        format_form = Form(self.env["barcodes.gs1.label.options.format"])
        format_form.name = "70 x 37 mm"
        format_form.paperformat_id = self.paperformat_a4_portrait
        format_form.label_width = 70
        self.assertEqual(format_form.page_max_labels, 0)
        format_form.label_height = 37
        self.assertEqual(format_form.page_max_labels, 24)

    def test_format_on_paper_without_size_raises(self):
        paperformat = self.env["report.paperformat"].create(
            {
                "name": "Paper without size",
                "format": False,
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
        with self.assertRaisesRegex(
            UserError, "The paperformat 'Paper without size' has no format defined"
        ):
            label_format.read(["page_max_labels"])

    def test_format_on_paper_without_orientation_raises(self):
        paperformat = self.env["report.paperformat"].create(
            {
                "name": "Paper without orientation",
                "format": "A4",
                "orientation": False,
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
        with self.assertRaisesRegex(
            UserError,
            "The paperformat 'Paper without orientation' has no orientation defined",
        ):
            label_format.read(["page_max_labels"])

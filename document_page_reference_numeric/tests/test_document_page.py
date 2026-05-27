# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDocumentPageReference(TransactionCase):
    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        self.category = self.DocumentPage.create(
            {"name": "Test Category", "type": "category"}
        )

    def _create_page(self, **vals):
        defaults = {
            "name": "Test Page",
            "type": "content",
            "parent_id": self.category.id,
        }
        defaults.update(vals)
        return self.DocumentPage.create(defaults)

    def test_reference_auto_generated_as_10_digits(self):
        page = self._create_page()
        self.assertTrue(page.reference, "Reference should be auto-generated")
        self.assertEqual(
            len(page.reference), 10, "Reference should be exactly 10 digits long"
        )
        self.assertTrue(page.reference.isdigit(), "Reference should be all digits")

    def test_manual_reference_is_preserved(self):
        page = self._create_page(reference="legacy_code_001")
        self.assertEqual(page.reference, "legacy_code_001")

    def test_manual_numeric_reference_is_preserved(self):
        page = self._create_page(reference="1799534795")
        self.assertEqual(page.reference, "1799534795")

    def test_uniqueness_among_auto_generated(self):
        pages = self.env["document.page"]
        for i in range(20):
            pages |= self._create_page(name="Page %d" % i)
        refs = pages.mapped("reference")
        self.assertEqual(
            len(refs), len(set(refs)), "Auto-generated references must be unique"
        )

    def test_duplicate_reference_rejected(self):
        self._create_page(reference="1234567890")
        with self.assertRaises(ValidationError):
            self._create_page(name="Another Page", reference="1234567890")

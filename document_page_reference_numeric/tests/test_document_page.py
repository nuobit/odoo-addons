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
        with self.assertRaisesRegex(ValidationError, "unique"):
            self._create_page(name="Another Page", reference="1234567890")

    def test_reference_at_int4_max_rejected(self):
        with self.assertRaisesRegex(ValidationError, "too large"):
            self._create_page(reference="2147483647")

    def test_reference_just_below_int4_max_accepted(self):
        page = self._create_page(reference="2147483646")
        self.assertEqual(page.reference, "2147483646")

    def test_post_init_hook_seeds_sequence_above_legacy_max(self):
        from odoo.addons.document_page_reference_numeric.hooks import post_init_hook

        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        original_next = sequence.number_next_actual
        try:
            self._create_page(name="Legacy High", reference="2000000000")
            post_init_hook(self.env.cr, self.env.registry)
            sequence.invalidate_cache(["number_next_actual"], sequence.ids)
            self.assertGreater(
                sequence.number_next_actual,
                2000000000,
                "Hook must advance the sequence above the highest legacy reference",
            )
            page = self._create_page(name="After Seed")
            self.assertTrue(page.reference.isdigit())
            self.assertGreater(int(page.reference), 2000000000)
        finally:
            sequence.number_next_actual = original_next

    def test_sequence_is_company_global(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        self.assertFalse(
            sequence.company_id,
            "Sequence must be global (company_id=False) so numeric references "
            "are generated in every company, not only the install company",
        )

    def test_reference_numeric_in_other_company(self):
        main_company = self.env.ref("base.main_company")
        other_company = self.env["res.company"].search(
            [("id", "!=", main_company.id)], limit=1
        )
        if not other_company:
            self.skipTest("No second company in this database to test cross-company")
        page = self.DocumentPage.with_company(other_company).create(
            {
                "name": "Doc in other company",
                "type": "category",
                "company_id": other_company.id,
            }
        )
        self.assertTrue(
            page.reference and page.reference.isdigit(),
            "Reference must be a number (global sequence), not a title slug, "
            "in a company other than the one that installed the module",
        )
        self.assertEqual(len(page.reference), 10)

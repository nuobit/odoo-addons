# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
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

    def test_manual_large_numeric_reference_is_preserved(self):
        page = self._create_page(reference="5123456789")
        self.assertEqual(page.reference, "5123456789")

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

    def test_generated_reference_skips_existing_reference(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.number_next_actual = 1234567890
        self._create_page(name="Legacy Page", reference="1234567890")
        page = self._create_page(name="New Page")
        self.assertEqual(page.reference, "1234567891")

    def test_generated_reference_skips_archived_reference(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.number_next_actual = 1234567890
        archived_page = self._create_page(name="Archived Page", reference="1234567890")
        # Archived below the ORM: modules installed in the same database may add
        # rules to archiving, and this test only needs an archived page
        archived_page.flush()
        self.env.cr.execute(
            "UPDATE document_page SET active = FALSE WHERE id = %s",
            (archived_page.id,),
        )
        archived_page.invalidate_cache(fnames=["active"], ids=archived_page.ids)
        self.assertFalse(archived_page.active)
        page = self._create_page(name="New Page")
        self.assertEqual(page.reference, "1234567891")

    def test_generated_reference_skips_reference_of_other_company(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.number_next_actual = 1234567890
        other_company = self.env["res.company"].create(
            {"name": "Document Page Test Company"}
        )
        self._create_page(
            name="Other Company Page",
            reference="1234567890",
            company_id=other_company.id,
        )
        user = new_test_user(
            self.env,
            login="document_editor_test",
            groups="base.group_user,document_page.group_document_editor",
            context={"no_reset_password": True},
        )
        page = self.DocumentPage.with_user(user).create({"name": "New Page"})
        self.assertEqual(page.reference, "1234567891")

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
        other_company = self.env["res.company"].create(
            {"name": "Document Page Test Company"}
        )
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

    def test_archived_sequence_rejected(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.active = False
        with self.assertRaises(UserError) as error:
            self.DocumentPage.with_context(lang="en_US").create({"name": "Test Page"})
        self.assertEqual(
            str(error.exception),
            "There is no active sequence with code document.page.reference.numeric "
            "to generate a numeric reference. Type a reference, or ask an "
            "administrator to restore the sequence.",
        )

    def test_copy_gets_next_reference(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        page = self._create_page(reference="1799534795")
        sequence.number_next_actual = 42
        page_copy = page.copy()
        self.assertEqual(page_copy.reference, "0000000042")

    def test_cleared_reference_rejected(self):
        page = self._create_page(reference="1799534795")
        with self.assertRaises(ValidationError) as error:
            page.with_context(lang="en_US").write({"reference": False})
        self.assertEqual(
            str(error.exception), 'The reference of "Test Page" cannot be empty.'
        )

    def test_empty_text_reference_rejected(self):
        page = self._create_page(reference="1799534795")
        with self.assertRaises(ValidationError) as error:
            page.with_context(lang="en_US").write({"reference": ""})
        self.assertEqual(
            str(error.exception), 'The reference of "Test Page" cannot be empty.'
        )

    def test_page_without_reference_gets_next_number(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.number_next_actual = 42
        page = self._create_page()
        self.assertEqual(page.reference, "0000000042")

    def test_page_created_with_empty_reference_gets_next_number(self):
        sequence = self.env.ref(
            "document_page_reference_numeric.seq_document_page_reference_numeric"
        )
        sequence.number_next_actual = 42
        page = self._create_page(reference=False)
        self.assertEqual(page.reference, "0000000042")

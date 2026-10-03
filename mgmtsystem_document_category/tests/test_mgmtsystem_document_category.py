# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestMgmtsystemDocumentCategory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]
        self.category = self.page_model.create(
            {
                "name": "Operations",
                "type": "category",
                "mgmtsystem_category_type": "procedure",
            }
        )
        self.document = self.page_model.create(
            {
                "name": "Waste handling",
                "type": "content",
                "parent_id": self.category.id,
                "content": "Test",
            }
        )
        self.subcategory = self.page_model.create(
            {"name": "Laboratory", "type": "category", "parent_id": self.category.id}
        )
        self.nested_document = self.page_model.create(
            {
                "name": "Spill response",
                "type": "content",
                "parent_id": self.subcategory.id,
                "content": "Test",
            }
        )
        self.other_category = self.page_model.create(
            {"name": "Archive", "type": "category"}
        )
        self.other_document = self.page_model.create(
            {
                "name": "Old notes",
                "type": "content",
                "parent_id": self.other_category.id,
                "content": "Test",
            }
        )

    def test_search_documents_under_classified_category(self):
        """The flag finds the documents under a classified category at any depth,
        never a category nor a document of an unclassified category."""
        found = self.page_model.search([("is_mgmtsystem_document", "=", True)])
        self.assertIn(self.document, found)
        self.assertIn(self.nested_document, found)
        self.assertNotIn(self.category, found)
        self.assertNotIn(self.subcategory, found)
        self.assertNotIn(self.other_category, found)
        self.assertNotIn(self.other_document, found)

    def test_search_not_documents_under_classified_category(self):
        """The negated flag finds every other page."""
        found = self.page_model.search([("is_mgmtsystem_document", "=", False)])
        self.assertNotIn(self.document, found)
        self.assertNotIn(self.nested_document, found)
        self.assertIn(self.category, found)
        self.assertIn(self.subcategory, found)
        self.assertIn(self.other_category, found)
        self.assertIn(self.other_document, found)

    def test_search_not_false(self):
        """Searching the flag as not false finds what searching it as true finds."""
        self.assertEqual(
            self.page_model.search([("is_mgmtsystem_document", "!=", False)]),
            self.page_model.search([("is_mgmtsystem_document", "=", True)]),
        )

    def test_read_is_mgmtsystem_document(self):
        """The value read agrees with the search."""
        self.assertTrue(self.nested_document.is_mgmtsystem_document)
        self.assertFalse(self.subcategory.is_mgmtsystem_document)
        self.assertFalse(self.other_document.is_mgmtsystem_document)

    def test_search_unsupported_operator(self):
        """The flag is only searched as true or false."""
        with self.assertRaises(UserError) as error:
            self.page_model.with_context(lang="en_US").search(
                [("is_mgmtsystem_document", "in", [True])]
            )
        self.assertEqual(
            error.exception.args[0],
            "Management System Document can only be searched as true or false.",
        )

    def test_search_unsupported_value(self):
        """The flag is only compared with true or false."""
        with self.assertRaises(UserError) as error:
            self.page_model.with_context(lang="en_US").search(
                [("is_mgmtsystem_document", "=", 1)]
            )
        self.assertEqual(
            error.exception.args[0],
            "Management System Document can only be searched as true or false.",
        )

    def test_classify_content_page(self):
        """A content page cannot have a management system category type."""
        page = self.page_model.create(
            {"name": "Content page", "type": "content", "content": "Test"}
        )
        with self.assertRaises(ValidationError) as error:
            page.with_context(lang="en_US").write(
                {"mgmtsystem_category_type": "procedure"}
            )
        self.assertEqual(
            error.exception.args[0],
            'The page "Content page" is not a category: only a category can '
            "have a Management System Category Type.",
        )

    def test_retype_classified_category(self):
        """A classified category cannot become a content page."""
        with self.assertRaises(ValidationError) as error:
            self.category.with_context(lang="en_US").write({"type": "content"})
        self.assertEqual(
            error.exception.args[0],
            'The page "Operations" is not a category: only a category can '
            "have a Management System Category Type.",
        )

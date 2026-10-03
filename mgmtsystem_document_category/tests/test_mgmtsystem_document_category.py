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

    def _offered_procedures(self):
        # The domain the web client applies to the procedures picker, resolved
        # server-side from the field's callable domain.
        domain = self.env["mgmtsystem.nonconformity"].fields_get(["procedure_ids"])[
            "procedure_ids"
        ]["domain"]
        return self.page_model.search(domain)

    def test_documents_under_classified_category_are_offered(self):
        """Documents under a classified category are offered at any depth,
        regardless of the category name or language; documents under an
        unclassified category are not."""
        category = self.page_model.create(
            {"name": "Procedimientos", "type": "category"}
        )
        category.mgmtsystem_category_type = "procedure"
        document = self.page_model.create(
            {
                "name": "Procedure document",
                "type": "content",
                "parent_id": category.id,
                "content": "Test",
            }
        )
        subcategory = self.page_model.create(
            {"name": "Subfolder", "type": "category", "parent_id": category.id}
        )
        nested_document = self.page_model.create(
            {
                "name": "Nested procedure document",
                "type": "content",
                "parent_id": subcategory.id,
                "content": "Test",
            }
        )
        other_category = self.page_model.create({"name": "Other", "type": "category"})
        other_document = self.page_model.create(
            {
                "name": "Unrelated document",
                "type": "content",
                "parent_id": other_category.id,
                "content": "Test",
            }
        )
        offered = self._offered_procedures()
        self.assertIn(document, offered)
        self.assertIn(nested_document, offered)
        self.assertNotIn(other_document, offered)

    def test_unclassified_category_documents_not_offered(self):
        """A document under an unclassified category is never offered."""
        category = self.page_model.create({"name": "Unclassified", "type": "category"})
        document = self.page_model.create(
            {
                "name": "Unclassified document",
                "type": "content",
                "parent_id": category.id,
                "content": "Test",
            }
        )
        self.assertNotIn(document, self._offered_procedures())

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

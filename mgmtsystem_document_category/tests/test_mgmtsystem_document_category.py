# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMgmtsystemDocumentCategory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]

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

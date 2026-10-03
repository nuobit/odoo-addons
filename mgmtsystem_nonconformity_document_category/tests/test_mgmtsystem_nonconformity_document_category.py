# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestMgmtsystemNonconformityDocumentCategory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.page_model = self.env["document.page"]

    def _procedures_domain(self):
        # The domain the procedures picker of the nonconformity form carries
        view = self.env["mgmtsystem.nonconformity"].fields_view_get(
            view_id=self.env.ref(
                "mgmtsystem_nonconformity.view_mgmtsystem_nonconformity_form"
            ).id,
            view_type="form",
        )
        [node] = etree.fromstring(view["arch"]).xpath("//field[@name='procedure_ids']")
        return safe_eval(node.get("domain"))

    def test_procedures_offered(self):
        """The procedures offered are the documents under a classified category,
        at any depth; never a category nor a document of another category."""
        category = self.page_model.create(
            {
                "name": "Operations",
                "type": "category",
                "mgmtsystem_category_type": "procedure",
            }
        )
        document = self.page_model.create(
            {
                "name": "Waste handling",
                "type": "content",
                "parent_id": category.id,
                "content": "Test",
            }
        )
        subcategory = self.page_model.create(
            {"name": "Laboratory", "type": "category", "parent_id": category.id}
        )
        nested_document = self.page_model.create(
            {
                "name": "Spill response",
                "type": "content",
                "parent_id": subcategory.id,
                "content": "Test",
            }
        )
        other_category = self.page_model.create({"name": "Archive", "type": "category"})
        other_document = self.page_model.create(
            {
                "name": "Old notes",
                "type": "content",
                "parent_id": other_category.id,
                "content": "Test",
            }
        )
        offered = self.page_model.search(self._procedures_domain())
        self.assertIn(document, offered)
        self.assertIn(nested_document, offered)
        self.assertNotIn(category, offered)
        self.assertNotIn(subcategory, offered)
        self.assertNotIn(other_category, offered)
        self.assertNotIn(other_document, offered)

    def test_category_classified_after_opening_the_form(self):
        """A category classified after the form was opened offers its documents
        at the next search."""
        domain = self._procedures_domain()
        category = self.page_model.create({"name": "Operations", "type": "category"})
        document = self.page_model.create(
            {
                "name": "Waste handling",
                "type": "content",
                "parent_id": category.id,
                "content": "Test",
            }
        )
        category.mgmtsystem_category_type = "procedure"
        self.assertIn(document, self.page_model.search(domain))

    def test_other_type_documents_offered(self):
        """The documents of a category of another type are flagged and offered."""
        category = self.page_model.create(
            {
                "name": "Environment",
                "type": "category",
                "mgmtsystem_category_type": "environment_manual",
            }
        )
        document = self.page_model.create(
            {
                "name": "Emissions",
                "type": "content",
                "parent_id": category.id,
                "content": "Test",
            }
        )
        self.assertIn(
            document, self.page_model.search([("is_mgmtsystem_document", "=", True)])
        )
        self.assertIn(document, self.page_model.search(self._procedures_domain()))

    def test_oca_procedure_category_classified(self):
        """The install classifies the OCA procedure category as a procedure."""
        self.assertEqual(
            self.env.ref(
                "document_page_procedure.document_page_group_procedure"
            ).mgmtsystem_category_type,
            "procedure",
        )

    def test_oca_procedure_category_documents_offered(self):
        """After the install, the documents of the OCA procedure category are
        offered."""
        document = self.page_model.create(
            {
                "name": "Waste handling",
                "type": "content",
                "parent_id": self.env.ref(
                    "document_page_procedure.document_page_group_procedure"
                ).id,
                "content": "Test",
            }
        )
        self.assertIn(document, self.page_model.search(self._procedures_domain()))

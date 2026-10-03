# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestMgmtsystemAuditDocumentCategory(TransactionCase):
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

    def _procedures_domain(self, view_xmlid, view_type):
        # The domain the web client gives the procedure picker of a
        # verification line view: the one of the field node, or the field's
        # own when the node has none.
        view = self.env["mgmtsystem.verification.line"].fields_view_get(
            view_id=self.env.ref(view_xmlid).id, view_type=view_type
        )
        [node] = etree.fromstring(view["arch"]).xpath("//field[@name='procedure_id']")
        domain = node.get("domain")
        if domain:
            return safe_eval(domain)
        return view["fields"]["procedure_id"]["domain"]

    def test_form_procedures_offered(self):
        """The verification line form offers the documents under a classified
        category, at any depth; never a category nor a document of another
        category."""
        offered = self.page_model.search(
            self._procedures_domain(
                "mgmtsystem_audit.view_mgmtsystem_verification_line_form", "form"
            )
        )
        self.assertIn(self.document, offered)
        self.assertIn(self.nested_document, offered)
        self.assertNotIn(self.category, offered)
        self.assertNotIn(self.subcategory, offered)
        self.assertNotIn(self.other_category, offered)
        self.assertNotIn(self.other_document, offered)

    def test_search_view_procedures_offered(self):
        """The verification line search offers the same documents."""
        offered = self.page_model.search(
            self._procedures_domain(
                "mgmtsystem_audit.view_mgmtsystem_verification_line_filter", "search"
            )
        )
        self.assertIn(self.document, offered)
        self.assertIn(self.nested_document, offered)
        self.assertNotIn(self.category, offered)
        self.assertNotIn(self.subcategory, offered)
        self.assertNotIn(self.other_category, offered)
        self.assertNotIn(self.other_document, offered)

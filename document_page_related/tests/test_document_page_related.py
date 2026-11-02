# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageRelated(TransactionCase):
    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        self.category = self.DocumentPage.create(
            {"name": "Test Category", "type": "category"}
        )
        self.editor = self.env["res.users"].create(
            {
                "name": "Editor",
                "login": "editor_related_test",
                "groups_id": [
                    (6, 0, [self.env.ref("document_page.group_document_editor").id])
                ],
            }
        )

    def _create_page(self, **vals):
        defaults = {
            "name": "Test Page",
            "type": "content",
            "parent_id": self.category.id,
        }
        defaults.update(vals)
        return self.DocumentPage.create(defaults)

    def _archive_page(self, page):
        # Archived below the ORM: modules installed in the same database may add
        # rules to archiving, and these tests only need an archived page
        page.flush()
        self.env.cr.execute(
            "UPDATE document_page SET active = FALSE WHERE id = %s", (page.id,)
        )
        page.invalidate_cache(fnames=["active"], ids=page.ids)

    def test_reader_sees_related_documents_tab_last_on_documents(self):
        reader = self.env["res.users"].create(
            {
                "name": "Reader",
                "login": "reader_related_test",
                "groups_id": [
                    (6, 0, [self.env.ref("knowledge.group_document_user").id])
                ],
            }
        )
        arch = self.DocumentPage.with_user(reader).fields_view_get(view_type="form")[
            "arch"
        ]
        tabs = etree.fromstring(arch).xpath("//notebook/page")
        self.assertEqual(tabs[-1].get("name"), "related_documents")
        # In 14.0 a group the reader lacks hides the tab (invisible: true) instead of
        # removing it: the tab shows on documents and hides on categories
        invisible = json.loads(tabs[-1].get("modifiers"))["invisible"]
        law = self._create_page(name="Law")
        self.assertFalse(law.filtered_domain(invisible))
        self.assertEqual(self.category.filtered_domain(invisible), self.category)

    def test_editor_adds_related_document(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.with_user(self.editor).write({"related_page_ids": [(4, law.id)]})
        self.assertEqual(procedure.related_page_ids, law)

    def test_editor_removes_related_document(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self.assertEqual(procedure.related_page_ids, law)
        procedure.with_user(self.editor).write({"related_page_ids": [(3, law.id)]})
        self.assertFalse(procedure.related_page_ids)
        self.assertFalse(law.related_from_page_ids)

    def test_related_document_lists_the_documents_relating_it(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self.assertEqual(law.related_from_page_ids, procedure)

    def test_open_page_opens_the_document_form(self):
        law = self._create_page(name="Law")
        action = law.action_open_page()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "document.page")
        self.assertEqual(action["res_id"], law.id)
        self.assertEqual(action["target"], "current")

    def test_editor_edit_keeps_related_document_hidden_from_editor(self):
        other_company = self.env["res.company"].create(
            {"name": "Document Page Related Test Company"}
        )
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(name="Hidden Law", company_id=other_company.id)
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        # each request of the editor starts with an empty cache
        procedure.invalidate_cache()
        procedure_as_editor = procedure.with_user(self.editor)
        self.assertFalse(procedure_as_editor.related_page_ids)
        procedure_as_editor.write({"related_page_ids": [(6, 0, [guide.id])]})
        procedure.invalidate_cache()
        self.assertEqual(procedure.related_page_ids, guide | hidden_law)

    def test_archived_related_document_is_not_listed(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        self.assertFalse(procedure.related_page_ids)

    def test_unarchived_related_document_is_listed_again(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        law.action_unarchive()
        self.assertEqual(procedure.related_page_ids, law)

    def test_copy_keeps_related_documents(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        procedure_copy = procedure.copy()
        self.assertEqual(procedure_copy.related_page_ids, law)

    def test_copy_of_related_document_is_not_related(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        law.copy()
        self.assertEqual(procedure.related_page_ids, law)

    def test_document_related_to_itself_raises(self):
        procedure = self._create_page(name="Procedure")
        with self.assertRaises(ValidationError) as ctx:
            procedure.write({"related_page_ids": [(4, procedure.id)]})
        self.assertEqual(
            str(ctx.exception),
            "A document cannot be related to itself: Procedure",
        )

    def test_document_related_to_itself_through_related_from_raises(self):
        law = self._create_page(name="Law")
        with self.assertRaises(ValidationError) as ctx:
            law.write({"related_from_page_ids": [(4, law.id)]})
        self.assertEqual(
            str(ctx.exception),
            "A document cannot be related to itself: Law",
        )

    def test_archived_document_related_to_itself_raises(self):
        law = self._create_page(name="Law")
        self._archive_page(law)
        with self.assertRaises(ValidationError) as ctx:
            law.write({"related_page_ids": [(4, law.id)]})
        self.assertEqual(
            str(ctx.exception),
            "A document cannot be related to itself: Law",
        )

    def test_related_category_raises(self):
        procedure = self._create_page(name="Procedure")
        with self.assertRaises(ValidationError) as ctx:
            procedure.write({"related_page_ids": [(4, self.category.id)]})
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category.",
        )

    def test_category_related_through_related_from_raises(self):
        procedure = self._create_page(name="Procedure")
        with self.assertRaises(ValidationError) as ctx:
            self.category.write({"related_from_page_ids": [(4, procedure.id)]})
        self.assertEqual(
            str(ctx.exception),
            "A category cannot have related documents: Test Category",
        )

    def test_archived_category_related_raises(self):
        procedure = self._create_page(name="Procedure")
        self._archive_page(self.category)
        with self.assertRaises(ValidationError) as ctx:
            procedure.write({"related_page_ids": [(4, self.category.id)]})
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category.",
        )

    def test_related_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        with self.assertRaises(ValidationError) as ctx:
            law.write({"type": "category"})
        self.assertEqual(
            str(ctx.exception),
            "A category cannot have related documents: Law",
        )

    def test_document_with_archived_related_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        with self.assertRaises(ValidationError) as ctx:
            procedure.write({"type": "category"})
        self.assertEqual(
            str(ctx.exception),
            "A category cannot have related documents: Procedure",
        )

    def test_document_with_hidden_related_document_turned_into_category_raises(self):
        other_company = self.env["res.company"].create(
            {"name": "Document Page Related Test Company"}
        )
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(name="Hidden Law", company_id=other_company.id)
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        # each request of the editor starts with an empty cache
        procedure.invalidate_cache()
        with self.assertRaises(ValidationError) as ctx:
            procedure.with_user(self.editor).write({"type": "category"})
        self.assertEqual(
            str(ctx.exception),
            "A category cannot have related documents: Procedure",
        )

    def test_document_with_hidden_related_emptied_and_turned_into_category_raises(self):
        other_company = self.env["res.company"].create(
            {"name": "Document Page Related Test Company"}
        )
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(name="Hidden Law", company_id=other_company.id)
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        # each request of the editor starts with an empty cache
        procedure.invalidate_cache()
        # emptying the list keeps the link the editor cannot see
        with self.assertRaises(ValidationError) as ctx:
            procedure.with_user(self.editor).write(
                {"type": "category", "related_page_ids": [(6, 0, [])]}
            )
        self.assertEqual(
            str(ctx.exception),
            "A category cannot have related documents: Procedure",
        )

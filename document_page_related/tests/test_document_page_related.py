# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import Form, TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestDocumentPageRelated(TransactionCase):
    def setUp(self):
        super().setUp()
        # the tests check English messages
        self.env = self.env(context=dict(self.env.context, lang="en_US"))
        self.page_model = self.env["document.page"]
        self.category = self.page_model.create(
            {"name": "Test Category", "type": "category"}
        )
        self.other_company = self.env["res.company"].create({"name": "Other Company"})
        self.editor = self._create_user(
            "editor_test", "document_page.group_document_editor"
        )
        self.reader = self._create_user("reader_test", "knowledge.group_document_user")

    def _create_user(self, login, group):
        return self.env["res.users"].create(
            {
                "name": login,
                "login": login,
                "email": "%s@example.com" % login,
                "groups_id": [(6, 0, [self.env.ref(group).id])],
            }
        )

    def _create_page(self, **vals):
        defaults = {
            "name": "Test Page",
            "type": "content",
            "parent_id": self.category.id,
            "content": "<p>Text</p>",
            "draft_name": "1.0",
            "draft_summary": "First version",
        }
        defaults.update(vals)
        return self.page_model.create(defaults)

    def _archive_page(self, page):
        # Archived below the ORM: modules installed in the same database may add
        # rules to archiving, and these tests only need an archived page
        page.flush()
        self.env.cr.execute(
            "UPDATE document_page SET active = FALSE WHERE id = %s", (page.id,)
        )
        page.invalidate_cache(fnames=["active"], ids=page.ids)

    def _as_user(self, user, page):
        # each request of a user starts with nothing pending and an empty cache
        page.flush()
        page.invalidate_cache()
        return page.with_user(user)

    def _get_all_related_pages(self, page):
        # in the database: archived and hidden from the editor included
        page.invalidate_cache()
        return page.sudo().with_context(active_test=False).related_page_ids

    def test_reader_sees_related_documents_tab_last_on_documents(self):
        # a tab that another module adds with the default priority, installed later
        self.env["ir.ui.view"].create(
            {
                "name": "document.page.form.inherit.later",
                "model": "document.page",
                "inherit_id": self.env.ref("document_page.view_wiki_form").id,
                "arch": """
                    <xpath expr="//notebook" position="inside">
                        <page name="later" string="Later" />
                    </xpath>
                """,
            }
        )
        arch = self.page_model.with_user(self.reader).fields_view_get(view_type="form")[
            "arch"
        ]
        tabs = etree.fromstring(arch).xpath("//notebook/page")
        self.assertIn("later", [tab.get("name") for tab in tabs])
        self.assertEqual(tabs[-1].get("name"), "related_documents")
        # In 14.0 a group the reader lacks hides the tab (invisible: true) instead of
        # removing it: the tab shows on documents and hides on categories
        invisible = json.loads(tabs[-1].get("modifiers"))["invisible"]
        law = self._create_page(name="Law")
        self.assertFalse(law.filtered_domain(invisible))
        self.assertEqual(self.category.filtered_domain(invisible), self.category)

    def test_reader_reads_and_opens_but_does_not_edit(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        procedure_as_reader = self._as_user(self.reader, procedure)
        self.assertEqual(procedure_as_reader.related_page_ids, law)
        action = procedure_as_reader.related_page_ids.action_open_page()
        self.assertEqual(action["res_id"], law.id)
        with self.assertRaises(AccessError):
            procedure_as_reader.write({"related_page_ids": [(6, 0, [])]})

    def test_editor_adds_and_removes_related_document_in_the_form(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        with Form(self._as_user(self.editor, procedure)) as form:
            form.related_page_ids.add(law)
        self.assertEqual(procedure.related_page_ids, law)
        with Form(self._as_user(self.editor, procedure)) as form:
            form.related_page_ids.remove(law.id)
        self.assertFalse(procedure.related_page_ids)

    def test_related_document_does_not_list_the_documents_relating_it(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self.assertFalse(self._as_user(self.editor, law).related_page_ids)

    def test_related_document_has_a_list_of_its_own(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._as_user(self.editor, law).write(
            {"related_page_ids": [(6, 0, [procedure.id, guide.id])]}
        )
        self.assertEqual(law.related_page_ids, procedure | guide)
        self.assertEqual(procedure.related_page_ids, law)

    def test_editor_of_related_document_does_not_write_the_list_of_another(self):
        procedure = self._create_page(
            name="Procedure", company_id=self.other_company.id
        )
        law = self._create_page(name="Law")
        # the list is written only from the document it belongs to: there is no
        # field for the other side, which the rights on that document do not cover
        with self.assertRaises(ValueError):
            self._as_user(self.editor, law).write(
                {"related_from_page_ids": [(4, procedure.id)]}
            )
        self.assertFalse(self._get_all_related_pages(procedure))

    def test_list_offers_only_other_documents(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        domain = self.page_model.fields_get(["related_page_ids"])["related_page_ids"][
            "domain"
        ]
        offered = (procedure | law | self.category).filtered_domain(
            safe_eval(domain, {"id": procedure.id})
        )
        self.assertEqual(offered, law)

    def test_open_page_opens_the_document_form(self):
        law = self._create_page(name="Law")
        action = self._as_user(self.editor, law).action_open_page()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "document.page")
        self.assertEqual(action["res_id"], law.id)
        self.assertEqual(action["target"], "current")

    def test_editor_edit_makes_no_version(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        history = self.env["document.page.history"]
        domain = [("page_id", "=", procedure.id)]
        versions = history.search(domain)
        self.assertTrue(versions)
        self._as_user(self.editor, procedure).write({"related_page_ids": [(4, law.id)]})
        procedure.flush()
        self.assertEqual(history.search(domain), versions)

    def test_editor_edit_keeps_related_document_hidden_from_editor(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        procedure_as_editor = self._as_user(self.editor, procedure)
        self.assertFalse(procedure_as_editor.related_page_ids)
        procedure_as_editor.write({"related_page_ids": [(6, 0, [guide.id])]})
        self.assertEqual(self._get_all_related_pages(procedure), guide | hidden_law)

    def test_editor_edit_keeps_hidden_related_document_read_before_by_superuser(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        procedure_as_editor = self._as_user(self.editor, procedure)
        # another module reads the list as superuser in the same transaction
        self.assertEqual(procedure.sudo().related_page_ids, hidden_law)
        procedure_as_editor.write({"related_page_ids": [(6, 0, [guide.id])]})
        self.assertEqual(procedure_as_editor.related_page_ids, guide)
        self.assertEqual(self._get_all_related_pages(procedure), guide | hidden_law)

    def test_superuser_reads_hidden_related_document_after_editor_edit(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        self._as_user(self.editor, procedure).write(
            {"related_page_ids": [(6, 0, [guide.id])]}
        )
        # another module reads the list as superuser in the same transaction
        self.assertEqual(procedure.sudo().related_page_ids, guide | hidden_law)

    def test_editor_edit_leaves_hidden_related_document_unreadable(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        self._as_user(self.editor, procedure).write(
            {"related_page_ids": [(4, guide.id)]}
        )
        with self.assertRaises(AccessError):
            hidden_law.with_user(self.editor).mapped("name")

    def test_archived_related_document_is_not_listed(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        self.assertFalse(self._as_user(self.editor, procedure).related_page_ids)

    def test_editor_edit_keeps_archived_related_document(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        self._as_user(self.editor, procedure).write(
            {"related_page_ids": [(6, 0, [guide.id])]}
        )
        law.action_unarchive()
        procedure.invalidate_cache()
        self.assertEqual(procedure.related_page_ids, guide | law)

    def test_deleted_related_document_leaves_the_others(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        guide = self._create_page(name="Guide")
        procedure.write({"related_page_ids": [(6, 0, [law.id, guide.id])]})
        law.unlink()
        self.assertEqual(self._get_all_related_pages(procedure), guide)

    def test_copy_keeps_related_documents_the_copying_user_can_read(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        archived_law = self._create_page(name="Archived Law")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        procedure.write(
            {"related_page_ids": [(6, 0, (law | archived_law | hidden_law).ids)]}
        )
        self._archive_page(archived_law)
        procedure_copy = self._as_user(self.editor, procedure).copy()
        self.assertEqual(
            self._get_all_related_pages(procedure_copy), law | archived_law
        )

    def test_copy_leaves_out_hidden_related_document_read_before_by_superuser(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        procedure.write({"related_page_ids": [(6, 0, [law.id, hidden_law.id])]})
        procedure_as_editor = self._as_user(self.editor, procedure)
        # another module reads the list as superuser in the same transaction
        self.assertEqual(procedure.sudo().related_page_ids, law | hidden_law)
        procedure_copy = procedure_as_editor.copy()
        self.assertEqual(self._get_all_related_pages(procedure_copy), law)

    def test_copy_of_related_document_is_not_related(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._as_user(self.editor, law).copy()
        self.assertEqual(self._get_all_related_pages(procedure), law)

    def test_document_related_to_itself_raises(self):
        procedure = self._create_page(name="Procedure")
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, procedure).write(
                {"related_page_ids": [(4, procedure.id)]}
            )
        self.assertEqual(
            str(ctx.exception),
            "A document cannot be related to itself: Procedure",
        )

    def test_archived_document_related_to_itself_raises(self):
        law = self._create_page(name="Law")
        self._archive_page(law)
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, law).write({"related_page_ids": [(4, law.id)]})
        self.assertEqual(
            str(ctx.exception),
            "A document cannot be related to itself: Law",
        )

    def test_related_category_raises(self):
        procedure = self._create_page(name="Procedure")
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, procedure).write(
                {"related_page_ids": [(4, self.category.id)]}
            )
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category. Remove the categories from "
            "its list first; some may be archived or hidden from you.",
        )

    def test_archived_category_related_raises(self):
        procedure = self._create_page(name="Procedure")
        self._archive_page(self.category)
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, procedure).write(
                {"related_page_ids": [(4, self.category.id)]}
            )
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category. Remove the categories from "
            "its list first; some may be archived or hidden from you.",
        )

    def test_hidden_category_related_raises(self):
        procedure = self._create_page(name="Procedure")
        hidden_category = self.page_model.create(
            {
                "name": "Hidden Category",
                "type": "category",
                "company_id": self.other_company.id,
            }
        )
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, procedure).write(
                {"related_page_ids": [(4, hidden_category.id)]}
            )
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category. Remove the categories from "
            "its list first; some may be archived or hidden from you.",
        )

    def test_create_related_to_category_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, self.page_model).create(
                {
                    "name": "Procedure",
                    "type": "content",
                    "parent_id": self.category.id,
                    "content": "<p>Text</p>",
                    "draft_name": "1.0",
                    "draft_summary": "First version",
                    "related_page_ids": [(4, self.category.id)],
                }
            )
        self.assertEqual(
            str(ctx.exception),
            "Procedure cannot be related to a category. Remove the categories from "
            "its list first; some may be archived or hidden from you.",
        )

    def test_import_related_to_category_is_refused(self):
        result = self._as_user(self.editor, self.page_model).load(
            ["name", "type", "parent_id/.id", "related_page_ids/.id"],
            [["Procedure", "content", str(self.category.id), str(self.category.id)]],
        )
        self.assertFalse(result["ids"])
        self.assertEqual(
            [message["message"] for message in result["messages"]],
            [
                "Procedure cannot be related to a category. Remove the categories "
                "from its list first; some may be archived or hidden from you."
            ],
        )

    def test_document_without_links_turned_into_category(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        guide = self._create_page(name="Guide")
        self._as_user(self.editor, guide).write({"type": "category"})
        self.assertEqual(guide.type, "category")

    def test_category_with_related_document_raises(self):
        law = self._create_page(name="Law")
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, self.category).write(
                {"related_page_ids": [(4, law.id)]}
            )
        self.assertEqual(
            str(ctx.exception),
            "Test Category has related documents, so it cannot be a category. Remove "
            "them first; some may be archived or hidden from you.",
        )

    def test_related_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, law).write({"type": "category"})
        self.assertEqual(
            str(ctx.exception),
            "Law is a related document of other documents, so it cannot be a "
            "category. Remove it from their lists first; some of those documents may "
            "be archived or hidden from you.",
        )

    def test_document_related_by_archived_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(procedure)
        with self.assertRaises(ValidationError):
            self._as_user(self.editor, law).write({"type": "category"})

    def test_document_related_by_hidden_document_turned_into_category_raises(self):
        hidden_procedure = self._create_page(
            name="Hidden Procedure", company_id=self.other_company.id
        )
        law = self._create_page(name="Law")
        hidden_procedure.write({"related_page_ids": [(4, law.id)]})
        with self.assertRaises(ValidationError):
            self._as_user(self.editor, law).write({"type": "category"})

    def test_document_with_archived_related_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        law = self._create_page(name="Law")
        procedure.write({"related_page_ids": [(4, law.id)]})
        self._archive_page(law)
        with self.assertRaises(ValidationError) as ctx:
            self._as_user(self.editor, procedure).write({"type": "category"})
        self.assertEqual(
            str(ctx.exception),
            "Procedure has related documents, so it cannot be a category. Remove "
            "them first; some may be archived or hidden from you.",
        )

    def test_document_with_hidden_related_document_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        with self.assertRaises(ValidationError):
            self._as_user(self.editor, procedure).write({"type": "category"})

    def test_document_with_hidden_related_emptied_and_turned_into_category_raises(self):
        procedure = self._create_page(name="Procedure")
        hidden_law = self._create_page(
            name="Hidden Law", company_id=self.other_company.id
        )
        procedure.write({"related_page_ids": [(4, hidden_law.id)]})
        # emptying the list keeps the link the editor cannot see
        with self.assertRaises(ValidationError):
            self._as_user(self.editor, procedure).write(
                {"type": "category", "related_page_ids": [(6, 0, [])]}
            )

# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageEditable(TransactionCase):
    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        group_editable = self.env.ref(
            "document_page_editable_file.group_document_editable_file"
        )
        group_reader = self.env.ref("knowledge.group_document_user")
        group_editor = self.env.ref("document_page.group_document_editor")
        group_manager = self.env.ref("document_page.group_document_manager")
        # With an email, as the users of the tests of Odoo: Odoo posts no message
        # without the email of its author, and a module such as
        # document_page_approval posts one when a version is saved
        users = self.env["res.users"].with_context(no_reset_password=True)
        self.member = users.create(
            {
                "name": "Member",
                "login": "member_dpef_test",
                "email": "member_dpef_test@example.com",
                "groups_id": [(6, 0, [group_editable.id])],
            }
        )
        self.editor_member = users.create(
            {
                "name": "Editor Member",
                "login": "editor_member_dpef_test",
                "email": "editor_member_dpef_test@example.com",
                "groups_id": [(6, 0, [group_editable.id, group_editor.id])],
            }
        )
        self.editor = users.create(
            {
                "name": "Editor",
                "login": "editor_dpef_test",
                "email": "editor_dpef_test@example.com",
                "groups_id": [(6, 0, [group_editor.id])],
            }
        )
        self.manager = users.create(
            {
                "name": "Manager",
                "login": "manager_dpef_test",
                "email": "manager_dpef_test@example.com",
                "groups_id": [(6, 0, [group_manager.id])],
            }
        )
        self.reader = users.create(
            {
                "name": "Reader",
                "login": "reader_dpef_test",
                "email": "reader_dpef_test@example.com",
                "groups_id": [(6, 0, [group_reader.id])],
            }
        )
        self.category = self.DocumentPage.create(
            {"name": "Procedures", "type": "category"}
        )
        self.page = self.DocumentPage.create(
            {
                "name": "Procedure",
                "type": "content",
                "parent_id": self.category.id,
                "draft_name": "1.0",
                "draft_summary": "First version",
                "content": "<p>Version one</p>",
                "editable_content": "<p>procedure.docx</p>",
            }
        )

    def _page_form_arch(self, user):
        view = self.env.ref("document_page.view_wiki_form")
        result = self.DocumentPage.with_user(user).fields_view_get(
            view_id=view.id, view_type="form"
        )
        return etree.fromstring(result["arch"])

    def _version_form_arch(self, user):
        view = self.env.ref("document_page.wiki_history_form")
        result = (
            self.env["document.page.history"]
            .with_user(user)
            .fields_view_get(view_id=view.id, view_type="form")
        )
        return etree.fromstring(result["arch"])

    def test_knowledge_role_picker_stays_a_selection(self):
        # A group of its own in the category of Knowledge ties with Editor, and the
        # form of the user then shows the roles of Knowledge as checkboxes
        knowledge = self.env.ref("knowledge.module_category_knowledge")
        kinds = {
            application: kind
            for application, kind, _groups, _name in self.env[
                "res.groups"
            ].get_groups_by_application()
        }
        self.assertEqual(kinds[knowledge], "selection")

    def test_reader_form_has_no_editables_tab(self):
        arch = self._page_form_arch(self.reader)
        self.assertFalse(arch.xpath("//page[@name='editable_files']"))
        self.assertFalse(arch.xpath("//field[@name='editable_content']"))

    def test_member_form_has_editable_content_in_tab(self):
        arch = self._page_form_arch(self.member)
        self.assertTrue(
            arch.xpath("//page[@name='editable_files']/field[@name='editable_content']")
        )

    def test_manager_form_has_editable_content_in_tab(self):
        arch = self._page_form_arch(self.manager)
        self.assertTrue(
            arch.xpath("//page[@name='editable_files']/field[@name='editable_content']")
        )

    def test_editables_tab_right_after_history(self):
        # The manager also gets the Security tab, which document_page_access_group
        # puts after History too
        arch = self._page_form_arch(self.manager)
        self.assertEqual(
            arch.xpath("//page[@name='history']/following-sibling::page[1]/@name"),
            ["editable_files"],
        )

    def test_reader_version_form_has_no_editables_tab(self):
        arch = self._version_form_arch(self.reader)
        self.assertFalse(arch.xpath("//page[@name='editable_files']"))

    def test_member_version_form_has_editables_tab_last(self):
        # document_page_distribution, when it is installed, adds its tab at the end
        # of the notebook too: ours goes after it
        arch = self._version_form_arch(self.member)
        self.assertEqual(
            arch.xpath("//notebook/page[last()]/@name"), ["editable_files"]
        )

    def test_manager_version_form_has_editables_tab(self):
        arch = self._version_form_arch(self.manager)
        self.assertTrue(arch.xpath("//page[@name='editable_files']"))

    def test_reader_cannot_read_editable_content(self):
        # The page created in setUp is in the cache of every environment: without
        # emptying it, the read below would not check the groups of the field
        self.page.invalidate_cache()
        page = self.page.with_user(self.reader)
        self.assertNotIn("editable_content", page.fields_get())
        with self.assertRaises(AccessError):
            page.read(["editable_content"])

    def test_editor_member_saves_editable_content_with_the_document(self):
        form = Form(
            self.page.with_user(self.editor_member),
            view="document_page.view_wiki_form",
        )
        form.editable_content = "<p>procedure_v2.docx</p>"
        form.save()
        self.assertIn("procedure_v2.docx", self.page.editable_content)

    def test_new_version_keeps_the_editable_content_saved_with_it(self):
        first_version = self.page.history_head
        form = Form(
            self.page.with_user(self.editor_member),
            view="document_page.view_wiki_form",
        )
        form.content = "<p>Version two</p>"
        form.editable_content = "<p>procedure_v2.docx</p>"
        form.save()
        self.assertNotEqual(self.page.history_head, first_version)
        self.assertIn("procedure_v2.docx", self.page.history_head.editable_content)
        self.assertNotIn("procedure_v2.docx", first_version.editable_content)

    def test_editable_content_saved_alone_goes_to_the_current_version(self):
        version = self.page.history_head
        form = Form(
            self.page.with_user(self.editor_member),
            view="document_page.view_wiki_form",
        )
        form.editable_content = "<p>procedure_v2.docx</p>"
        form.save()
        self.assertEqual(self.page.history_head, version)
        self.assertIn("procedure_v2.docx", version.editable_content)

    def test_editor_saves_a_new_version_with_the_editable_content(self):
        # The editor cannot read the editable content, and the new version keeps it
        # all the same. The page created in setUp is in the cache of every
        # environment: without emptying it, the save would not check the groups of
        # the field
        first_version = self.page.history_head
        self.page.invalidate_cache()
        form = Form(
            self.page.with_user(self.editor),
            view="document_page.view_wiki_form",
        )
        form.content = "<p>Version two</p>"
        form.save()
        self.assertNotEqual(self.page.history_head, first_version)
        self.assertIn("procedure.docx", self.page.history_head.editable_content)

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import sys

from odoo.exceptions import AccessError, UserError
from odoo.modules.module import load_information_from_description_file
from odoo.tests import Form, SavepointCase, tagged

EDITABLE_FILE = "document.page.editable.file"
APPROVAL_LOCK = (
    'The editable files of "Procedure #%d" cannot change: under approval, only '
    "those of a draft change request can."
)
SHOWN_VERSION_LOCK = (
    'The editable files of "Procedure #%d" cannot change: only those of the '
    "version its document shows can."
)
# Odoo's refusal of a list a form keeps read-only
NOT_EDITABLE = "field editable_file_ids is not editable"


def encoded(text):
    """The content of a file, as a binary field takes it."""
    return base64.b64encode(text.encode())


@tagged("post_install", "-at_install")
class TestDocumentPageEditableFileApproval(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The messages the tests read are in English, as the web client asks them
        cls.env = cls.env(context=dict(cls.env.context, lang="en_US"))
        cls.author = cls._new_user(
            "author_test", cls.env.ref("document_page.group_document_editor")
        )
        cls.editor = cls._new_user(
            "editor_test", cls.env.ref("document_page.group_document_editor")
        )
        cls.approver = cls._new_user(
            "approver_test",
            cls.env.ref("document_page_approval.group_document_approver_user"),
        )
        DocumentPage = cls.env["document.page"]
        cls.category = DocumentPage.create({"name": "Procedures", "type": "category"})
        # Approval is not required yet: the first version is approved at once
        cls.page = DocumentPage.create(
            {
                "name": "Procedure",
                "type": "content",
                "parent_id": cls.category.id,
                "draft_name": "1.0",
                "draft_summary": "First version",
                "content": "<p>Version one</p>",
            }
        )
        cls.version = cls.page.history_head
        cls.procedure_file = cls.env[EDITABLE_FILE].create(
            {
                "history_id": cls.version.id,
                "sequence": 10,
                "name": "procedure.docx",
                "file": encoded("Word source of the procedure"),
            }
        )
        cls.page.approval_required = True

    @classmethod
    def _new_user(cls, login, groups):
        """A user of ``groups``."""
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "email": "%s@example.com" % login,
                    "groups_id": [(6, 0, groups.ids)],
                }
            )
        )

    def _new_draft(self, user=None):
        """A change request ``user``, the author unless given, creates from Change
        Requests, a draft."""
        form = Form(
            self.env["document.page.history"]
            .with_user(user or self.author)
            .with_context(default_page_id=self.page.id),
            view="document_page.wiki_history_form",
        )
        form.name = "2.0"
        form.content = "<p>Version two</p>"
        return form.save()

    def _attachment_of(self, editable_file):
        """The attachment that keeps the content of ``editable_file``."""
        return self.env["ir.attachment"].search(
            [
                ("res_model", "=", EDITABLE_FILE),
                ("res_id", "=", editable_file.id),
                ("res_field", "=", "file"),
            ]
        )

    def _mark_to_remove(self, *modules):
        """Mark ``modules`` to remove, as Odoo does before it runs their uninstall
        hooks, those of the modules that depend on others first."""
        self.env["ir.module.module"].search([("name", "in", modules)]).write(
            {"state": "to remove"}
        )

    def _run_uninstall_hook(self, module):
        """Run the uninstall hook of ``module`` as Odoo finds it when it uninstalls
        the module: the function its manifest names, in the module's package.
        Where Odoo skips a manifest that names none, this fails."""
        hook = load_information_from_description_file(module)["uninstall_hook"]
        getattr(sys.modules["odoo.addons.%s" % module], hook)(
            self.env.cr, self.env.registry
        )

    def test_the_shown_version_is_approved_and_its_document_requires_approval(self):
        self.assertEqual(self.version.state, "approved")
        self.assertTrue(self.page.is_approval_required)

    def test_draft_starts_with_the_shown_files_and_changes_them(self):
        draft = self._new_draft()
        self.assertEqual(draft.state, "draft")
        self.assertEqual(draft.editable_file_ids.mapped("name"), ["procedure.docx"])
        with Form(
            draft.with_user(self.author), view="document_page.wiki_history_form"
        ) as form:
            with form.editable_file_ids.new() as line:
                line.sequence = 20
                line.name = "checklist.docx"
                line.file = encoded("Checklist")
        draft.with_user(self.author).action_to_approve()
        draft.with_user(self.approver).action_approve()
        self.assertEqual(self.page.history_head, draft)
        self.assertEqual(
            self.page.editable_file_ids.mapped("name"),
            ["procedure.docx", "checklist.docx"],
        )
        self.assertEqual(self.version.editable_file_ids, self.procedure_file)

    def test_content_change_sends_a_change_request_with_the_shown_files(self):
        self.page.with_user(self.author).write({"content": "<p>Version two</p>"})
        request = self.env["document.page.history"].search(
            [("page_id", "=", self.page.id), ("state", "=", "to approve")]
        )
        self.assertEqual(len(request), 1)
        self.assertEqual(request.editable_file_ids.mapped("name"), ["procedure.docx"])
        self.assertEqual(self.page.history_head, self.version)

    def test_a_request_sent_for_approval_keeps_its_files_read_only(self):
        draft = self._new_draft()
        self.assertFalse(draft.editables_locked)
        draft.with_user(self.author).action_to_approve()
        self.assertTrue(draft.editables_locked)

    def test_files_cannot_change_once_sent_for_approval(self):
        draft = self._new_draft()
        draft.with_user(self.author).action_to_approve()
        self.assertEqual(draft.state, "to approve")
        with self.assertRaises(UserError) as error:
            draft.editable_file_ids.with_user(self.author).write({"name": "late.docx"})
        self.assertEqual(str(error.exception), APPROVAL_LOCK % draft.id)

    def test_a_request_cancelled_and_back_to_draft_changes_its_files(self):
        draft = self._new_draft()
        draft.with_user(self.author).action_to_approve()
        draft.with_user(self.author).action_cancel()
        self.assertEqual(draft.state, "cancelled")
        self.assertTrue(draft.editables_locked)
        draft.with_user(self.author).action_draft()
        self.assertEqual(draft.state, "draft")
        self.assertFalse(draft.editables_locked)
        draft.editable_file_ids.with_user(self.author).write({"name": "revised.docx"})
        self.assertEqual(draft.editable_file_ids.mapped("name"), ["revised.docx"])

    def test_approved_files_cannot_change_where_approval_is_required(self):
        with self.assertRaises(UserError) as error:
            self.procedure_file.with_user(self.editor).write({"name": "late.docx"})
        self.assertEqual(str(error.exception), APPROVAL_LOCK % self.version.id)

    def test_shown_files_change_where_approval_is_not_required(self):
        self.page.approval_required = False
        self.procedure_file.with_user(self.editor).write({"name": "procedure_v1.docx"})
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        new_version = self.page.history_head
        self.assertNotEqual(new_version, self.version)
        self.assertEqual(new_version.state, "approved")
        with self.assertRaises(UserError) as error:
            self.procedure_file.with_user(self.editor).write({"name": "late.docx"})
        self.assertEqual(str(error.exception), SHOWN_VERSION_LOCK % self.version.id)

    def test_the_list_of_the_document_is_read_only_where_approval_is_required(self):
        self.assertTrue(self.page.editables_locked)
        form = Form(
            self.page.with_user(self.author), view="document_page.view_wiki_form"
        )
        with self.assertRaises(AssertionError) as error:
            form.editable_file_ids.new()
        self.assertEqual(str(error.exception), NOT_EDITABLE)

    def test_approved_files_cannot_change_through_the_document(self):
        with self.assertRaises(UserError) as error:
            self.page.with_user(self.editor).write(
                {
                    "editable_file_ids": [
                        (1, self.procedure_file.id, {"name": "late.docx"})
                    ]
                }
            )
        self.assertEqual(str(error.exception), APPROVAL_LOCK % self.version.id)
        self.assertEqual(self.procedure_file.name, "procedure.docx")

    def test_the_document_changes_its_files_where_approval_is_not_required(self):
        self.page.approval_required = False
        self.assertFalse(self.page.editables_locked)
        self.page.with_user(self.editor).write(
            {
                "content": "<p>Version two</p>",
                "editable_file_ids": [
                    (1, self.procedure_file.id, {"name": "procedure_v2.docx"})
                ],
            }
        )
        new_version = self.page.history_head
        self.assertNotEqual(new_version, self.version)
        self.assertEqual(
            new_version.editable_file_ids.mapped("name"), ["procedure_v2.docx"]
        )
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"), ["procedure.docx"]
        )

    def test_a_document_awaiting_its_first_approval_keeps_its_list_read_only(self):
        page = self.env["document.page"].new(
            {"type": "content", "approval_required": True}
        )
        self.assertTrue(page.editables_locked)

    def test_other_editor_does_not_reach_the_files_of_a_draft(self):
        draft = self._new_draft()
        draft.with_user(self.author).write(
            {
                "editable_file_ids": [
                    (0, 0, {"name": "draft.docx", "file": encoded("Draft source")})
                ]
            }
        )
        copied_file = self.env[EDITABLE_FILE].search(
            [("history_id", "=", draft.id), ("name", "=", "procedure.docx")]
        )
        draft_file = self.env[EDITABLE_FILE].search(
            [("history_id", "=", draft.id), ("name", "=", "draft.docx")]
        )
        domain = [("history_id.page_id", "=", self.page.id)]
        self.assertEqual(
            self.env[EDITABLE_FILE].with_user(self.author).search(domain).ids,
            [self.procedure_file.id, copied_file.id, draft_file.id],
        )
        files = self.env[EDITABLE_FILE].with_user(self.editor)
        self.assertEqual(files.search(domain), self.procedure_file)
        self.env[EDITABLE_FILE].invalidate_cache()
        with self.assertRaises(AccessError) as read:
            draft_file.with_user(self.editor).read(["name"])
        with self.assertRaises(AccessError) as written:
            draft_file.with_user(self.editor).write({"name": "renamed.docx"})
        download = (
            self.env["ir.http"]
            .with_user(self.editor)
            .binary_content(model=EDITABLE_FILE, id=draft_file.id, field="file")
        )
        self.assertIn("(%s)" % EDITABLE_FILE, str(read.exception))
        self.assertIn("(%s)" % EDITABLE_FILE, str(written.exception))
        self.assertEqual(download[0], 403)

    def test_editor_names_no_draft_of_another_author_by_its_id(self):
        # The API hands its caller's context to create: another author's draft
        # given there by its id, under either key, is no origin, so its files
        # reach no one the draft does not reach
        draft = self._new_draft()
        draft.with_user(self.author).write(
            {
                "editable_file_ids": [
                    (0, 0, {"name": "draft.docx", "file": encoded("Draft source")})
                ]
            }
        )
        self.assertEqual(
            draft.editable_file_ids.mapped("name"), ["procedure.docx", "draft.docx"]
        )
        self.env["document.page.history"].invalidate_cache()
        with self.assertRaises(AccessError):
            draft.with_user(self.editor).read(["name"])
        versions = (
            self.env["document.page.history"]
            .with_user(self.editor)
            .with_context(default_page_id=self.page.id)
        )
        for key in ("editable_files_origin", "editable_files_origin_id"):
            with self.subTest(key=key):
                request = versions.with_context(**{key: draft.id}).create(
                    {"name": "3.0", "content": "<p>Changed under %s</p>" % key}
                )
                self.assertEqual(request.state, "draft")
                self.assertEqual(
                    request.editable_file_ids.mapped("name"), ["procedure.docx"]
                )

    def test_editor_cannot_move_a_file_into_a_draft_of_another_author(self):
        # Odoo checks the rules of a write on the files as they were. Two reads
        # refuse the move: this module's lock reads the other draft's state as the
        # user, and the first module's check of the file reads the moved file as
        # the user. Neither may become a read as superuser
        draft = self._new_draft()
        own_draft = self._new_draft(self.editor)
        self.assertEqual(own_draft.state, "draft")
        self.assertEqual(own_draft.create_uid, self.editor)
        own_file = own_draft.editable_file_ids
        self.assertEqual(own_file.mapped("name"), ["procedure.docx"])
        self.assertEqual(own_file.history_id, own_draft)
        draft_files = draft.editable_file_ids
        self.assertEqual(draft_files.mapped("name"), ["procedure.docx"])
        # Saved, as the versions of an earlier request are: the rules read the
        # database
        draft.flush()
        draft.invalidate_cache()
        with self.assertRaises(AccessError):
            draft.with_user(self.editor).read(["name"])
        # The savepoint rolls back what the refused write did, as its request would
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            own_file.with_user(self.editor).write({"history_id": draft.id})
        self.assertEqual(own_file.history_id, own_draft)
        self.assertEqual(draft.editable_file_ids, draft_files)

    def test_approver_reaches_the_files_of_a_request_sent_for_approval(self):
        draft = self._new_draft()
        domain = [("history_id", "=", draft.id)]
        self.assertFalse(
            self.env[EDITABLE_FILE].with_user(self.approver).search(domain)
        )
        draft.with_user(self.author).action_to_approve()
        self.env[EDITABLE_FILE].invalidate_cache()
        self.assertEqual(
            self.env[EDITABLE_FILE].with_user(self.approver).search(domain),
            draft.editable_file_ids,
        )
        self.assertFalse(self.env[EDITABLE_FILE].with_user(self.editor).search(domain))

    def test_deleting_a_document_deletes_the_files_of_its_change_requests(self):
        draft = self._new_draft()
        self.assertNotIn(draft, self.page.history_ids)
        draft_file = draft.editable_file_ids
        self.assertEqual(draft_file.mapped("name"), ["procedure.docx"])
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", EDITABLE_FILE),
                ("res_id", "in", [self.procedure_file.id, draft_file.id]),
                ("res_field", "=", "file"),
            ]
        )
        self.assertEqual(len(attachments), 2)
        self.page.unlink()
        self.assertFalse(self.procedure_file.exists())
        self.assertFalse(draft_file.exists())
        self.assertFalse(attachments.exists())

    def test_uninstalling_approval_deletes_the_files_of_its_change_requests(self):
        draft = self._new_draft()
        draft_file = draft.editable_file_ids
        self.assertEqual(draft_file.mapped("name"), ["procedure.docx"])
        draft_attachment = self._attachment_of(draft_file)
        shown_attachment = self._attachment_of(self.procedure_file)
        self.assertEqual(len(draft_attachment), 1)
        self.assertEqual(len(shown_attachment), 1)
        self._mark_to_remove(
            "document_page_editable_file_approval", "document_page_approval"
        )
        self._run_uninstall_hook("document_page_editable_file_approval")
        self._run_uninstall_hook("document_page_approval")
        self.assertFalse(draft.exists())
        self.assertFalse(draft_attachment.exists())
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(shown_attachment.exists())

    def test_uninstalling_this_module_alone_keeps_the_files_of_change_requests(self):
        draft = self._new_draft()
        draft_attachment = self._attachment_of(draft.editable_file_ids)
        self.assertEqual(len(draft_attachment), 1)
        self._mark_to_remove("document_page_editable_file_approval")
        self._run_uninstall_hook("document_page_editable_file_approval")
        self.assertEqual(draft.editable_file_ids.mapped("name"), ["procedure.docx"])
        self.assertTrue(draft_attachment.exists())

    def test_uninstalling_approval_keeps_the_files_of_a_version_with_no_state(self):
        # Code or SQL can leave a version with no state; approval's hook keeps it,
        # since SQL reads «state != 'approved'» as false there
        self.env["document.page.history"].flush()
        self.env.cr.execute(
            "UPDATE document_page_history SET state = NULL WHERE id = %s",
            [self.version.id],
        )
        self.env["document.page.history"].invalidate_cache(["state"], self.version.ids)
        self.assertFalse(self.version.state)
        shown_attachment = self._attachment_of(self.procedure_file)
        self.assertEqual(len(shown_attachment), 1)
        self._mark_to_remove(
            "document_page_editable_file_approval", "document_page_approval"
        )
        self._run_uninstall_hook("document_page_editable_file_approval")
        self._run_uninstall_hook("document_page_approval")
        self.assertTrue(self.version.exists())
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(shown_attachment.exists())

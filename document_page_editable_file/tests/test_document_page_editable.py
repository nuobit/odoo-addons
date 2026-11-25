# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
import json

from lxml import etree
from PIL import Image

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form, SavepointCase, tagged

EDITABLE_FILE = "document.page.editable.file"
SHOWN_VERSION_LOCK = (
    'The editable files of "Procedure #%d" cannot change: only those of the '
    "version its document shows can."
)
ATTACHMENT_REFUSAL = (
    "The attachment of an editable file cannot be changed directly: change the "
    "file on the Editables tab of its version, while its files can change."
)
# Odoo's refusals: of a list a form keeps read-only, and of a stale record
NOT_EDITABLE = "field editable_file_ids is not editable"
CONCURRENCY_REFUSAL = "A document was modified since you last viewed it (%s:%d)"


def encoded(text):
    """The content of a file, as a binary field takes it."""
    return base64.b64encode(text.encode())


@tagged("post_install", "-at_install")
class TestDocumentPageEditable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The messages the tests read are in English, as the web client asks them
        cls.env = cls.env(context=dict(cls.env.context, lang="en_US"))
        cls.second_company = cls.env["res.company"].create(
            {"name": "Second company test"}
        )
        cls.reader = cls._new_user(
            "reader_test",
            cls.env.ref("knowledge.group_document_user"),
            cls.env.company,
        )
        cls.editor = cls._new_user(
            "editor_test",
            cls.env.ref("document_page.group_document_editor"),
            cls.env.company,
        )
        cls.manager = cls._new_user(
            "manager_test",
            cls.env.ref("document_page.group_document_manager"),
            cls.env.company,
        )
        DocumentPage = cls.env["document.page"]
        cls.category = DocumentPage.create({"name": "Procedures", "type": "category"})
        cls.page = (
            DocumentPage.with_user(cls.editor)
            .create(
                {
                    "name": "Procedure",
                    "type": "content",
                    "parent_id": cls.category.id,
                    "draft_name": "1.0",
                    "draft_summary": "First version",
                    "content": "<p>Version one</p>",
                }
            )
            .with_env(cls.env)
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
        cls.annex_file = cls.env[EDITABLE_FILE].create(
            {
                "history_id": cls.version.id,
                "sequence": 20,
                "name": "annex.xlsx",
                "file": encoded("Annex sheet"),
            }
        )

    @classmethod
    def _new_user(cls, login, groups, company):
        """A user of ``groups`` in ``company`` alone."""
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "email": "%s@example.com" % login,
                    "company_id": company.id,
                    "company_ids": [(6, 0, company.ids)],
                    "groups_id": [(6, 0, groups.ids)],
                }
            )
        )

    def _attachment_of(self, editable_file):
        """The attachment that keeps the content of ``editable_file``."""
        return self.env["ir.attachment"].search(
            [
                ("res_model", "=", EDITABLE_FILE),
                ("res_id", "=", editable_file.id),
                ("res_field", "=", "file"),
            ]
        )

    def _hidden_by(self, record, xpath):
        """Whether the element at ``xpath`` of the form an editor gets for
        ``record`` is hidden for that record."""
        arch = etree.fromstring(
            record.with_user(self.editor).fields_view_get(view_type="form")["arch"]
        )
        (element,) = arch.xpath(xpath)
        invisible = json.loads(element.get("modifiers")).get("invisible", False)
        return bool(record.filtered_domain(invisible)) if invisible else False

    def _ctid_of(self, page):
        """The place of the row of ``page`` in its table, which any update of the
        row moves."""
        self.env["document.page"].flush()
        self.env.cr.execute("SELECT ctid FROM document_page WHERE id = %s", [page.id])
        return self.env.cr.fetchone()[0]

    def test_editor_sees_the_shown_version_files_on_the_document(self):
        page = self.page.with_user(self.editor)
        page.invalidate_cache()
        self.assertIn(
            "editable_file_ids", page.fields_view_get(view_type="form")["fields"]
        )
        self.assertEqual(
            page.editable_file_ids.mapped("name"), ["procedure.docx", "annex.xlsx"]
        )

    def test_files_are_listed_in_their_order(self):
        self.env[EDITABLE_FILE].create(
            {
                "history_id": self.version.id,
                "sequence": 5,
                "name": "notes.txt",
                "file": encoded("Plain text notes"),
            }
        )
        self.assertEqual(
            self.env[EDITABLE_FILE]
            .search([("history_id", "=", self.version.id)])
            .mapped("name"),
            ["notes.txt", "procedure.docx", "annex.xlsx"],
        )

    def test_editor_downloads_an_editable_file(self):
        self.page.invalidate_cache()
        result = (
            self.env["ir.http"]
            .with_user(self.editor)
            .binary_content(
                model=EDITABLE_FILE, id=self.procedure_file.id, field="file"
            )
        )
        self.assertEqual(result[0], 200)
        self.assertEqual(base64.b64decode(result[2]), b"Word source of the procedure")

    def test_editor_opens_the_shown_version_from_the_document(self):
        action = self.page.with_user(self.editor).action_open_shown_version()
        self.assertEqual(
            action,
            {
                "type": "ir.actions.act_window",
                "res_model": "document.page.history",
                "res_id": self.version.id,
                "view_mode": "form",
            },
        )

    def test_a_category_has_no_version_to_open(self):
        with self.assertRaises(UserError) as error:
            self.category.with_user(self.editor).action_open_shown_version()
        self.assertEqual(
            str(error.exception),
            '"Procedures" shows no version yet: its editable files are kept with its '
            "versions.",
        )

    def test_the_editables_tab_shows_on_a_document_and_not_on_a_category(self):
        tab = "//page[@name='editable_files']"
        self.assertEqual(
            [self._hidden_by(self.page, tab), self._hidden_by(self.category, tab)],
            [False, True],
        )

    def test_the_button_shows_on_a_document_that_shows_a_version(self):
        page_without_version = self.env["document.page"].create(
            {"name": "Procedure to write", "type": "content"}
        )
        self.assertFalse(page_without_version.history_head)
        button = "//button[@name='action_open_shown_version']"
        self.assertEqual(
            [
                self._hidden_by(self.page, button),
                self._hidden_by(page_without_version, button),
            ],
            [False, True],
        )

    def test_reader_sees_no_editables_tab(self):
        tab = 'name="editable_files"'
        self.assertIn(tab, self.page.with_user(self.editor).fields_view_get()["arch"])
        self.assertNotIn(
            tab, self.page.with_user(self.reader).fields_view_get()["arch"]
        )
        self.assertNotIn(
            tab,
            self.version.with_user(self.reader).fields_view_get(view_type="form")[
                "arch"
            ],
        )

    def test_reader_gets_no_editables_field(self):
        self.assertIn(
            "editable_file_ids",
            self.env["document.page"].with_user(self.editor).fields_get(),
        )
        self.assertNotIn(
            "editable_file_ids",
            self.env["document.page"].with_user(self.reader).fields_get(),
        )
        self.assertNotIn(
            "editable_file_ids",
            self.env["document.page.history"].with_user(self.reader).fields_get(),
        )

    def test_reader_cannot_read_the_editables_through_the_api(self):
        self.page.invalidate_cache()
        with self.assertRaises(AccessError) as on_document:
            self.page.with_user(self.reader).read(["editable_file_ids"])
        with self.assertRaises(AccessError) as on_version:
            self.version.with_user(self.reader).read(["editable_file_ids"])
        with self.assertRaises(AccessError) as on_files:
            self.env[EDITABLE_FILE].with_user(self.reader).search([])
        self.assertIn("editable_file_ids", str(on_document.exception))
        self.assertIn("editable_file_ids", str(on_version.exception))
        self.assertIn("(%s)" % EDITABLE_FILE, str(on_files.exception))

    def test_reader_cannot_download_an_editable_file(self):
        attachment = self._attachment_of(self.procedure_file)
        self.assertEqual(len(attachment), 1)
        self.page.invalidate_cache()
        http = self.env["ir.http"].with_user(self.reader)
        by_field = http.binary_content(
            model=EDITABLE_FILE, id=self.procedure_file.id, field="file"
        )
        by_attachment = http.binary_content(id=attachment.id)
        self.assertEqual((by_field[0], by_attachment[0]), (403, 403))

    def test_reader_finds_no_editable_file_among_attachments(self):
        attachment = self._attachment_of(self.procedure_file)
        domain = [("res_model", "=", EDITABLE_FILE), ("res_field", "=", "file")]
        self.page.invalidate_cache()
        self.assertIn(
            attachment, self.env["ir.attachment"].with_user(self.editor).search(domain)
        )
        attachments = self.env["ir.attachment"].with_user(self.reader)
        self.assertFalse(attachments.search(domain))
        self.assertFalse(attachments.search([("id", "=", attachment.id)]))

    def test_reader_counts_no_editable_file_in_a_grouped_read(self):
        domain = [
            ("res_model", "=", EDITABLE_FILE),
            ("res_field", "=", "file"),
            ("res_id", "in", [self.procedure_file.id, self.annex_file.id]),
        ]
        self.page.invalidate_cache()
        as_reader = (
            self.env["ir.attachment"]
            .with_user(self.reader)
            .read_group(domain, ["res_id"], ["res_id"], lazy=False)
        )
        as_editor = (
            self.env["ir.attachment"]
            .with_user(self.editor)
            .read_group(domain, ["res_id"], ["res_id"], orderby="res_id", lazy=False)
        )
        self.assertEqual(as_reader, [])
        self.assertEqual(
            [group["res_id"] for group in as_editor],
            [self.procedure_file.id, self.annex_file.id],
        )

    def test_editor_of_another_company_tests_no_guess_in_a_grouped_read(self):
        self.page.company_id = self.env.company
        self._attachment_of(self.procedure_file).index_content = "alpha secret omega"
        second_company_editor = self._new_user(
            "second_company_editor_test",
            self.env.ref("document_page.group_document_editor"),
            self.second_company,
        )
        domain = [
            ("res_model", "=", EDITABLE_FILE),
            ("res_field", "=", "file"),
            ("res_id", "=", self.procedure_file.id),
            ("index_content", "ilike", "secret"),
        ]
        self.page.invalidate_cache()
        as_other_editor = (
            self.env["ir.attachment"]
            .with_user(second_company_editor)
            .read_group(domain, ["res_id"], ["res_id"], lazy=False)
        )
        as_editor = (
            self.env["ir.attachment"]
            .with_user(self.editor)
            .read_group(domain, ["res_id"], ["res_id"], lazy=False)
        )
        self.assertEqual(len(as_other_editor), 0)
        self.assertEqual(len(as_editor), 1)

    def test_editor_opens_a_group_of_a_grouped_read(self):
        attachments = self.env["ir.attachment"].with_user(self.editor)
        groups = attachments.read_group(
            [
                ("res_model", "=", EDITABLE_FILE),
                ("res_field", "=", "file"),
                ("res_id", "=", self.procedure_file.id),
            ],
            ["res_id"],
            ["res_id"],
            lazy=False,
        )
        # The client gets a group's domain as JSON and sends it back to open it
        domain = json.loads(json.dumps(groups[0]["__domain"]))
        self.assertEqual(
            attachments.search(domain), self._attachment_of(self.procedure_file)
        )

    def test_superuser_counts_an_attachment_left_by_a_deleted_file(self):
        left = self.env["ir.attachment"].create(
            {
                "name": "left.docx",
                "res_model": EDITABLE_FILE,
                "res_field": "file",
                "res_id": self.annex_file.id + 1000,
                "datas": encoded("Content of a file deleted"),
            }
        )
        groups = self.env["ir.attachment"].read_group(
            [("id", "=", left.id), ("res_field", "=", "file")],
            ["res_id"],
            ["res_id"],
            lazy=False,
        )
        self.assertEqual([group["__count"] for group in groups], [1])

    def test_reader_cannot_export_the_editables(self):
        self.reader.groups_id = [(4, self.env.ref("base.group_allow_export").id)]
        self.page.invalidate_cache()
        with self.assertRaises(AccessError) as on_document:
            self.page.with_user(self.reader).export_data(["editable_file_ids/id"])
        with self.assertRaises(AccessError) as on_version:
            self.version.with_user(self.reader).export_data(["editable_file_ids/name"])
        self.assertIn("editable_file_ids", str(on_document.exception))
        self.assertIn("editable_file_ids", str(on_version.exception))

    def test_reader_cannot_search_documents_or_versions_by_their_files(self):
        has_files = [("id", "=", self.page.id), ("editable_file_ids", "!=", False)]
        self.assertEqual(
            self.env["document.page"].with_user(self.editor).search(has_files),
            self.page,
        )
        pages = self.env["document.page"].with_user(self.reader)
        versions = self.env["document.page.history"].with_user(self.reader)
        with self.assertRaises(AccessError) as on_document:
            pages.search(has_files)
        with self.assertRaises(AccessError) as on_version:
            versions.search([("editable_file_ids", "in", [self.procedure_file.id])])
        with self.assertRaises(AccessError) as through_versions:
            pages.search([("history_ids.editable_file_ids", "!=", False)])
        # OCA's history_head has auto_join: Odoo joins the shown version
        with self.assertRaises(AccessError) as through_the_shown_version:
            pages.search([("history_head.editable_file_ids", "!=", False)])
        self.assertIn("editable_file_ids", str(on_document.exception))
        self.assertIn("editable_file_ids", str(on_version.exception))
        self.assertIn("editable_file_ids", str(through_versions.exception))
        self.assertIn("editable_file_ids", str(through_the_shown_version.exception))

    def test_editor_changes_the_files_of_the_shown_version(self):
        with Form(
            self.version.with_user(self.editor), view="document_page.wiki_history_form"
        ) as form:
            with form.editable_file_ids.new() as line:
                line.sequence = 30
                line.name = "notes.txt"
                line.file = encoded("Plain text notes")
            with form.editable_file_ids.edit(1) as line:
                line.file = encoded("Annex sheet, second edition")
            form.editable_file_ids.remove(0)
        files = self.version.editable_file_ids
        self.assertEqual(files.mapped("name"), ["annex.xlsx", "notes.txt"])
        self.assertEqual(
            [base64.b64decode(file.file) for file in files],
            [b"Annex sheet, second edition", b"Plain text notes"],
        )

    def test_a_large_image_is_kept_as_uploaded(self):
        image = io.BytesIO()
        Image.new("RGB", (2400, 1600), "white").save(image, "PNG")
        content = base64.b64encode(image.getvalue())
        image_file = (
            self.env[EDITABLE_FILE]
            .with_user(self.editor)
            .create(
                {"history_id": self.version.id, "name": "plan.png", "file": content}
            )
        )
        self.annex_file.with_user(self.editor).write({"file": content})
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        copied = self.env[EDITABLE_FILE].search(
            [("history_id", "=", self.page.history_head.id), ("name", "=", "plan.png")]
        )
        self.env[EDITABLE_FILE].invalidate_cache()
        self.assertEqual(image_file.file, content)
        self.assertEqual(self.annex_file.file, content)
        self.assertEqual(copied.file, content)

    def test_an_editable_file_needs_its_file(self):
        with self.assertRaises(ValidationError) as created:
            self.env[EDITABLE_FILE].with_user(self.editor).create(
                {"history_id": self.version.id, "name": "empty.docx"}
            )
        with self.assertRaises(ValidationError) as cleared:
            self.annex_file.with_user(self.editor).write({"file": False})
        self.assertEqual(
            str(created.exception),
            'The editable file "empty.docx" has no file: every editable file needs '
            "one.",
        )
        self.assertEqual(
            str(cleared.exception),
            'The editable file "annex.xlsx" has no file: every editable file needs '
            "one.",
        )

    def test_a_row_of_a_list_of_editable_files_opens_its_form(self):
        view = (
            self.env[EDITABLE_FILE]
            .with_user(self.editor)
            .fields_view_get(view_type="form")
        )
        self.assertEqual(
            view["view_id"],
            self.env.ref(
                "document_page_editable_file.document_page_editable_file_view_form"
            ).id,
        )

    def test_a_change_of_files_rewrites_their_document_row(self):
        before_write = self._ctid_of(self.page)
        self.annex_file.with_user(self.editor).write({"name": "annex_v1.xlsx"})
        after_write = self._ctid_of(self.page)
        notes_file = (
            self.env[EDITABLE_FILE]
            .with_user(self.editor)
            .create(
                {
                    "history_id": self.version.id,
                    "name": "notes.txt",
                    "file": encoded("Plain text notes"),
                }
            )
        )
        after_create = self._ctid_of(self.page)
        notes_file.unlink()
        after_unlink = self._ctid_of(self.page)
        self.assertNotEqual(after_write, before_write)
        self.assertNotEqual(after_create, after_write)
        self.assertNotEqual(after_unlink, after_create)

    def test_editor_of_another_company_does_not_see_the_files(self):
        self.page.company_id = self.env.company
        second_company_editor = self._new_user(
            "second_company_editor_test",
            self.env.ref("document_page.group_document_editor"),
            self.second_company,
        )
        self.page.invalidate_cache()
        files = self.env[EDITABLE_FILE].with_user(second_company_editor)
        self.assertFalse(
            files.search([("id", "in", [self.procedure_file.id, self.annex_file.id])])
        )

    def test_system_administrator_outside_the_knowledge_groups_cannot_read_them(self):
        administrator = self._new_user(
            "administrator_test",
            self.env.ref("base.group_system"),
            self.env.company,
        )
        with self.assertRaises(AccessError) as error:
            self.env[EDITABLE_FILE].with_user(administrator).search([])
        self.assertIn("(%s)" % EDITABLE_FILE, str(error.exception))

    def test_system_administrator_editor_changes_a_file_only_through_its_version(self):
        groups = self.env.ref("base.group_system")
        groups += self.env.ref("document_page.group_document_editor")
        administrator = self._new_user(
            "administrator_editor_test", groups, self.env.company
        )
        attachment = self._attachment_of(self.procedure_file).with_user(administrator)
        with self.assertRaises(AccessError) as written:
            attachment.write({"datas": encoded("Changed behind the version")})
        with self.assertRaises(AccessError) as linked:
            attachment.generate_access_token()
        with self.assertRaises(AccessError) as published:
            attachment.write({"public": True})
        with self.assertRaises(AccessError) as removed:
            attachment.unlink()
        with self.assertRaises(AccessError) as created:
            self.env["ir.attachment"].with_user(administrator).create(
                {
                    "name": "extra.docx",
                    "res_model": EDITABLE_FILE,
                    "res_field": "file",
                    "res_id": self.procedure_file.id,
                    "datas": encoded("Extra file"),
                }
            )
        self.assertEqual(str(written.exception), ATTACHMENT_REFUSAL)
        self.assertEqual(str(linked.exception), ATTACHMENT_REFUSAL)
        self.assertEqual(str(published.exception), ATTACHMENT_REFUSAL)
        self.assertEqual(str(removed.exception), ATTACHMENT_REFUSAL)
        self.assertEqual(str(created.exception), ATTACHMENT_REFUSAL)
        self.procedure_file.with_user(administrator).write(
            {"file": encoded("Changed through its version")}
        )
        self.procedure_file.invalidate_cache()
        self.assertEqual(
            base64.b64decode(self.procedure_file.file), b"Changed through its version"
        )

    def test_deleting_a_version_deletes_its_editable_files(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        other_file = self.page.history_head.editable_file_ids[0]
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        self.version.unlink()
        self.assertFalse(self.procedure_file.exists())
        self.assertFalse(self.annex_file.exists())
        self.assertFalse(attachments.exists())
        self.assertTrue(other_file.exists())
        self.assertEqual(len(self._attachment_of(other_file)), 1)

    def test_deleting_a_version_keeps_the_attachments_of_other_models(self):
        # Another model's file kept as an attachment, its field also named «file»
        # and its record's id that of an editable file the deletion removes
        other_attachment = self.env["ir.attachment"].create(
            {
                "name": "contract.pdf",
                "res_model": "res.partner",
                "res_field": "file",
                "res_id": self.procedure_file.id,
                "datas": encoded("A contact's contract"),
            }
        )
        self.version.unlink()
        self.assertFalse(self.procedure_file.exists())
        self.assertTrue(other_attachment.exists())

    def test_deleting_a_document_deletes_its_editable_files(self):
        other_page = self.env["document.page"].create(
            {
                "name": "Other procedure",
                "type": "content",
                "parent_id": self.category.id,
                "draft_name": "1.0",
                "draft_summary": "First version",
                "content": "<p>Other version one</p>",
            }
        )
        other_file = self.env[EDITABLE_FILE].create(
            {
                "history_id": other_page.history_head.id,
                "name": "other.docx",
                "file": encoded("File of another document"),
            }
        )
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        self.page.unlink()
        self.assertFalse(self.procedure_file.exists())
        self.assertFalse(self.annex_file.exists())
        self.assertFalse(attachments.exists())
        self.assertTrue(other_file.exists())
        self.assertEqual(len(self._attachment_of(other_file)), 1)

    def test_manager_deletes_a_document_with_a_superseded_version(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", EDITABLE_FILE),
                ("res_field", "=", "file"),
                ("res_id", "in", self.page.history_ids.editable_file_ids.ids),
            ]
        )
        self.assertEqual(len(attachments), 4)
        self.page.with_user(self.manager).unlink()
        self.assertFalse(self.page.exists())
        self.assertFalse(attachments.exists())

    def test_version_deleter_who_is_not_an_editor_deletes_a_version(self):
        # The right to delete versions, given in the database to a group of its own
        deleters = self.env["res.groups"].create({"name": "Version deleters test"})
        self.env["ir.model.access"].create(
            {
                "name": "document.page.history deleter test",
                "model_id": self.env["ir.model"]._get("document.page.history").id,
                "group_id": deleters.id,
                "perm_read": True,
                "perm_unlink": True,
            }
        )
        groups = deleters
        groups += self.env.ref("base.group_user")
        deleter = self._new_user("version_deleter_test", groups, self.env.company)
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        self.version.with_user(deleter).unlink()
        self.assertFalse(self.version.exists())
        self.assertFalse(attachments.exists())

    def test_editor_cannot_delete_a_document_and_its_files_stay(self):
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        with self.assertRaises(AccessError) as error:
            self.page.with_user(self.editor).unlink()
        self.assertIn("(document.page)", str(error.exception))
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_manager_cannot_delete_a_version_and_its_files_stay(self):
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        with self.assertRaises(AccessError) as error:
            self.version.with_user(self.manager).unlink()
        self.assertIn("(document.page.history)", str(error.exception))
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_manager_of_another_company_cannot_delete_a_document(self):
        self.page.company_id = self.env.company
        second_company_manager = self._new_user(
            "second_company_manager_test",
            self.env.ref("document_page.group_document_manager"),
            self.second_company,
        )
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        with self.assertRaises(AccessError) as error:
            self.page.with_user(second_company_manager).unlink()
        self.assertIn("(document.page)", str(error.exception))
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_version_deleter_of_another_company_cannot_delete_a_version(self):
        # The right to delete versions, given in the database to a group of its own
        self.page.company_id = self.env.company
        deleters = self.env["res.groups"].create({"name": "Version deleters test"})
        self.env["ir.model.access"].create(
            {
                "name": "document.page.history deleter test",
                "model_id": self.env["ir.model"]._get("document.page.history").id,
                "group_id": deleters.id,
                "perm_read": True,
                "perm_unlink": True,
            }
        )
        groups = deleters
        groups += self.env.ref("base.group_user")
        deleter = self._new_user(
            "second_company_deleter_test", groups, self.second_company
        )
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        with self.assertRaises(AccessError) as error:
            self.version.with_user(deleter).unlink()
        self.assertIn("(document.page.history)", str(error.exception))
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_files_stay_when_odoo_refuses_a_deletion_after_its_checks(self):
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        # A client that read the version before its last change
        stale = {
            "__last_update": {
                "document.page.history,%d" % self.version.id: "2000-01-01 00:00:00"
            }
        }
        with self.assertRaises(ValidationError) as error:
            self.version.with_context(**stale).unlink()
        self.assertEqual(
            str(error.exception),
            CONCURRENCY_REFUSAL % ("Document Page History", self.version.id),
        )
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_deleting_no_document_or_version_passes(self):
        self.assertTrue(self.env["document.page"].with_user(self.reader).unlink())
        self.assertTrue(
            self.env["document.page.history"].with_user(self.reader).unlink()
        )

    def test_new_version_starts_with_the_files_of_the_shown_version(self):
        with Form(
            self.page.with_user(self.editor), view="document_page.view_wiki_form"
        ) as form:
            form.content = "<p>Version two</p>"
            form.draft_name = "2.0"
            form.draft_summary = "Second version"
        new_version = self.page.history_head
        self.assertNotEqual(new_version, self.version)
        self.assertEqual(
            new_version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )
        self.assertEqual(new_version.editable_file_ids.mapped("sequence"), [10, 20])
        self.assertEqual(
            [base64.b64decode(file.file) for file in new_version.editable_file_ids],
            [b"Word source of the procedure", b"Annex sheet"],
        )
        self.assertEqual(
            self.version.editable_file_ids.ids,
            [self.procedure_file.id, self.annex_file.id],
        )

    def test_new_version_from_the_version_form_takes_the_shown_files(self):
        form = Form(
            self.env["document.page.history"]
            .with_user(self.editor)
            .with_context(default_page_id=self.page.id),
            view="document_page.wiki_history_form",
        )
        form.name = "2.0"
        form.content = "<p>Version two</p>"
        new_version = form.save()
        self.assertEqual(new_version.page_id, self.page)
        self.assertEqual(
            new_version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_unsaved_version_keeps_its_editables_read_only(self):
        form = Form(
            self.env["document.page.history"]
            .with_user(self.editor)
            .with_context(default_page_id=self.page.id),
            view="document_page.wiki_history_form",
        )
        with self.assertRaises(AssertionError) as error:
            form.editable_file_ids.new()
        self.assertEqual(str(error.exception), NOT_EDITABLE)

    def test_superseded_version_shows_its_files_read_only(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        form = Form(
            self.version.with_user(self.editor), view="document_page.wiki_history_form"
        )
        with self.assertRaises(AssertionError) as error:
            form.editable_file_ids.new()
        self.assertEqual(str(error.exception), NOT_EDITABLE)

    def test_writer_who_is_not_an_editor_keeps_the_files_without_seeing_them(self):
        writers = self.env["res.groups"].create({"name": "Document writers test"})
        for model in ("document.page", "document.page.history"):
            self.env["ir.model.access"].create(
                {
                    "name": "%s writer test" % model,
                    "model_id": self.env["ir.model"]._get(model).id,
                    "group_id": writers.id,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                }
            )
        self.reader.groups_id = [(4, writers.id)]
        self.page.with_user(self.reader).write({"content": "<p>Version two</p>"})
        new_version = self.page.history_head
        self.assertEqual(
            new_version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )
        new_version.invalidate_cache()
        with self.assertRaises(AccessError) as error:
            new_version.with_user(self.reader).read(["editable_file_ids"])
        self.assertIn("editable_file_ids", str(error.exception))

    def test_writer_who_is_not_an_editor_passing_no_files_keeps_them(self):
        writers = self.env["res.groups"].create({"name": "Document writers test"})
        self.env["ir.model.access"].create(
            {
                "name": "document.page.history writer test",
                "model_id": self.env["ir.model"]._get("document.page.history").id,
                "group_id": writers.id,
                "perm_read": True,
                "perm_create": True,
            }
        )
        self.reader.groups_id = [(4, writers.id)]
        new_version = (
            self.env["document.page.history"]
            .with_user(self.reader)
            .create(
                {
                    "page_id": self.page.id,
                    "content": "<p>Version two</p>",
                    "editable_file_ids": [],
                }
            )
        )
        self.assertEqual(
            new_version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_version_given_files_of_its_own_takes_no_copy(self):
        version = self.env["document.page.history"].create(
            {
                "page_id": self.page.id,
                "content": "<p>Version two</p>",
                "editable_file_ids": [
                    (0, 0, {"name": "form.odt", "file": encoded("Form to fill")})
                ],
            }
        )
        self.assertEqual(version.editable_file_ids.mapped("name"), ["form.odt"])

    def test_version_of_no_document_starts_without_editable_files(self):
        version = self.env["document.page.history"].create(
            {"name": "Loose", "content": "<p>A version of no document</p>"}
        )
        self.assertFalse(version.page_id)
        self.assertFalse(version.editable_file_ids)

    def test_duplicated_document_starts_without_editable_files(self):
        duplicate = self.page.with_user(self.editor).copy()
        self.assertTrue(duplicate.history_head)
        self.assertFalse(duplicate.history_head.editable_file_ids)

    def test_duplicated_version_keeps_the_files_of_its_source(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        shown_procedure_file = self.env[EDITABLE_FILE].search(
            [
                ("history_id", "=", self.page.history_head.id),
                ("name", "=", "procedure.docx"),
            ]
        )
        shown_procedure_file.with_user(self.editor).write({"name": "procedure_v2.docx"})
        duplicate = self.version.with_user(self.editor).copy()
        self.assertEqual(
            duplicate.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_duplicated_version_given_other_values_keeps_the_files_of_its_source(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        shown_procedure_file = self.env[EDITABLE_FILE].search(
            [
                ("history_id", "=", self.page.history_head.id),
                ("name", "=", "procedure.docx"),
            ]
        )
        shown_procedure_file.with_user(self.editor).write({"name": "procedure_v2.docx"})
        self.assertEqual(
            self.page.history_head.editable_file_ids.mapped("name"),
            ["procedure_v2.docx", "annex.xlsx"],
        )
        duplicate = self.version.with_user(self.editor).copy(
            default={"name": "1.0 copy"}
        )
        self.assertEqual(duplicate.name, "1.0 copy")
        self.assertEqual(
            duplicate.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_duplicated_version_given_no_files_keeps_the_files_of_its_source(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        shown_procedure_file = self.env[EDITABLE_FILE].search(
            [
                ("history_id", "=", self.page.history_head.id),
                ("name", "=", "procedure.docx"),
            ]
        )
        shown_procedure_file.with_user(self.editor).write({"name": "procedure_v2.docx"})
        self.assertEqual(
            self.page.history_head.editable_file_ids.mapped("name"),
            ["procedure_v2.docx", "annex.xlsx"],
        )
        for no_files in ([], False, [(5, 0, 0)]):
            with self.subTest(editable_file_ids=no_files):
                duplicate = self.version.with_user(self.editor).copy(
                    default={"editable_file_ids": no_files}
                )
                self.assertEqual(
                    duplicate.editable_file_ids.mapped("name"),
                    ["procedure.docx", "annex.xlsx"],
                )

    def test_duplicated_version_given_another_document_starts_with_its_files(self):
        other_page = self.env["document.page"].create(
            {"name": "Other procedure", "content": "<p>Other</p>"}
        )
        self.env[EDITABLE_FILE].create(
            {
                "history_id": other_page.history_head.id,
                "name": "other.docx",
                "file": encoded("Other source"),
            }
        )
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )
        duplicate = self.version.with_user(self.editor).copy(
            default={"page_id": other_page.id}
        )
        self.assertEqual(duplicate.page_id, other_page)
        self.assertEqual(duplicate.editable_file_ids.mapped("name"), ["other.docx"])

    def test_version_made_through_a_duplicate_starts_with_the_shown_files(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        duplicate = self.version.with_user(self.editor).copy()
        shown = self.page.history_head
        shown_procedure_file = self.env[EDITABLE_FILE].search(
            [("history_id", "=", shown.id), ("name", "=", "procedure.docx")]
        )
        shown_procedure_file.with_user(self.editor).write({"name": "procedure_v2.docx"})
        self.assertEqual(
            shown.editable_file_ids.mapped("name"), ["procedure_v2.docx", "annex.xlsx"]
        )
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )
        duplicate.page_id.write({"content": "<p>Version three</p>"})
        self.assertNotEqual(self.page.history_head, shown)
        self.assertEqual(
            self.page.history_head.editable_file_ids.mapped("name"),
            ["procedure_v2.docx", "annex.xlsx"],
        )

    def test_duplicated_version_given_files_of_its_own_keeps_only_them(self):
        duplicate = self.version.copy(
            default={
                "editable_file_ids": [
                    (0, 0, {"name": "form.odt", "file": encoded("Form to fill")})
                ]
            }
        )
        self.assertEqual(duplicate.editable_file_ids.mapped("name"), ["form.odt"])

    def test_editor_of_another_company_names_no_origin_by_its_id(self):
        # The API hands its caller's context to create: a version given there by
        # its id, under either key, is no origin
        self.page.company_id = self.env.company
        second_company_editor = self._new_user(
            "second_company_editor_test",
            self.env.ref("document_page.group_document_editor"),
            self.second_company,
        )
        # Saved, as the versions of an earlier request are: the rules read the
        # database
        self.version.flush()
        self.version.invalidate_cache()
        with self.assertRaises(AccessError):
            self.version.with_user(second_company_editor).read(["name"])
        own_page = self.env["document.page"].create(
            {
                "name": "Own procedure",
                "content": "<p>Own</p>",
                "company_id": self.second_company.id,
            }
        )
        self.env[EDITABLE_FILE].create(
            {
                "history_id": own_page.history_head.id,
                "name": "own.docx",
                "file": encoded("Own source"),
            }
        )
        versions = self.env["document.page.history"].with_user(second_company_editor)
        for key in ("editable_files_origin", "editable_files_origin_id"):
            with self.subTest(key=key):
                version = versions.with_context(**{key: self.version.id}).create(
                    {"page_id": own_page.id, "content": "<p>Own, under %s</p>" % key}
                )
                self.assertEqual(version.editable_file_ids.mapped("name"), ["own.docx"])

    def test_writer_who_is_not_an_editor_names_no_origin_by_its_id(self):
        # The document's write hands its caller's context to the version it makes:
        # an earlier version given there by its id, under either key, is no
        # origin, so the new version starts with the files the document showed
        writers = self.env["res.groups"].create({"name": "Document writers test"})
        for model in ("document.page", "document.page.history"):
            self.env["ir.model.access"].create(
                {
                    "name": "%s writer test" % model,
                    "model_id": self.env["ir.model"]._get(model).id,
                    "group_id": writers.id,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                }
            )
        self.reader.groups_id = [(4, writers.id)]
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        shown_procedure_file = self.env[EDITABLE_FILE].search(
            [
                ("history_id", "=", self.page.history_head.id),
                ("name", "=", "procedure.docx"),
            ]
        )
        shown_procedure_file.with_user(self.editor).write({"name": "procedure_v2.docx"})
        self.assertEqual(
            self.page.history_head.editable_file_ids.mapped("name"),
            ["procedure_v2.docx", "annex.xlsx"],
        )
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )
        page = self.page.with_user(self.reader)
        for key in ("editable_files_origin", "editable_files_origin_id"):
            with self.subTest(key=key):
                shown = self.page.history_head
                page.with_context(**{key: self.version.id}).write(
                    {"content": "<p>Changed under %s</p>" % key}
                )
                self.assertNotEqual(self.page.history_head, shown)
                self.assertEqual(
                    self.page.history_head.editable_file_ids.mapped("name"),
                    ["procedure_v2.docx", "annex.xlsx"],
                )

    def test_a_record_of_another_model_is_no_origin(self):
        version = (
            self.env["document.page.history"]
            .with_user(self.editor)
            .with_context(editable_files_origin=self.page)
            .create({"page_id": self.page.id, "content": "<p>Version two</p>"})
        )
        self.assertEqual(
            version.editable_file_ids.mapped("name"), ["procedure.docx", "annex.xlsx"]
        )

    def test_files_of_a_superseded_version_cannot_change(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        self.assertNotEqual(self.page.history_head, self.version)
        message = SHOWN_VERSION_LOCK % self.version.id
        version = self.version.with_user(self.editor)
        with self.assertRaises(UserError) as added:
            version.write(
                {
                    "editable_file_ids": [
                        (0, 0, {"name": "late.docx", "file": encoded("Late")})
                    ]
                }
            )
        with self.assertRaises(UserError) as renamed:
            self.procedure_file.with_user(self.editor).write({"name": "renamed.docx"})
        with self.assertRaises(UserError) as removed:
            self.procedure_file.with_user(self.editor).unlink()
        self.assertEqual(str(added.exception), message)
        self.assertEqual(str(renamed.exception), message)
        self.assertEqual(str(removed.exception), message)
        self.assertFalse(self.env[EDITABLE_FILE].search([("name", "=", "late.docx")]))
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_a_file_cannot_move_into_a_superseded_version(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        shown_file = self.env[EDITABLE_FILE].search(
            [("history_id", "=", self.page.history_head.id)], order="id", limit=1
        )
        with self.assertRaises(UserError) as error:
            shown_file.with_user(self.editor).write({"history_id": self.version.id})
        self.assertEqual(str(error.exception), SHOWN_VERSION_LOCK % self.version.id)

    def test_a_file_cannot_move_out_of_a_superseded_version(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        with self.assertRaises(UserError) as error:
            self.procedure_file.with_user(self.editor).write(
                {"history_id": self.page.history_head.id}
            )
        self.assertEqual(str(error.exception), SHOWN_VERSION_LOCK % self.version.id)

    def test_editor_cannot_move_a_file_into_a_version_of_another_company(self):
        # Odoo checks the rules of a write on the files as they were: the check of
        # the file, which reads the moved file as its user, is what refuses the
        # move, with approval installed too. That read must not become a read as
        # superuser
        other_page = self.env["document.page"].create(
            {
                "name": "Other company procedure",
                "content": "<p>Other</p>",
                "company_id": self.second_company.id,
            }
        )
        other_version = other_page.history_head
        # Saved, as the versions of an earlier request are: the rules read the
        # database
        other_version.flush()
        other_version.invalidate_cache()
        with self.assertRaises(AccessError):
            other_version.with_user(self.editor).read(["name"])
        # The savepoint rolls back what the refused write did, as its request would
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            self.procedure_file.with_user(self.editor).write(
                {"history_id": other_version.id}
            )
        self.assertEqual(self.procedure_file.history_id, self.version)
        self.assertFalse(other_version.editable_file_ids)

    def test_a_file_given_a_superseded_version_by_a_default_is_refused(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        files = (
            self.env[EDITABLE_FILE]
            .with_user(self.editor)
            .with_context(default_history_id=self.version.id)
        )
        with self.assertRaises(UserError) as error:
            files.create({"name": "late.docx", "file": encoded("Late")})
        self.assertEqual(str(error.exception), SHOWN_VERSION_LOCK % self.version.id)
        # The refused file is gone at once, not only once the request rolls back
        self.assertFalse(self.env[EDITABLE_FILE].search([("name", "=", "late.docx")]))
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_writing_no_file_passes(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        self.assertTrue(
            self.env[EDITABLE_FILE]
            .with_user(self.editor)
            .write({"history_id": self.version.id})
        )

    def test_superuser_changes_the_files_of_a_superseded_version(self):
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        self.procedure_file.write({"name": "procedure_v1.docx"})
        self.assertEqual(
            self.version.editable_file_ids.mapped("name"),
            ["procedure_v1.docx", "annex.xlsx"],
        )

    def test_editor_who_cannot_read_the_document_changes_its_shown_files(self):
        # A rule that hides the document, as document_page_access_group does for an
        # editor outside its groups. A global one: Odoo joins the rules of groups
        # with OR, so that a rule of a group would not hide it where another
        # module's rule of a group shows it, such as document_page_access_group's
        self.env["ir.rule"].create(
            {
                "name": "Hidden procedure test",
                "model_id": self.env["ir.model"]._get("document.page").id,
                "domain_force": "[('name', '!=', 'Procedure')]",
            }
        )
        self.page.invalidate_cache()
        with self.assertRaises(AccessError):
            self.page.with_user(self.editor).read(["name"])
        self.procedure_file.with_user(self.editor).write({"name": "renamed.docx"})
        self.assertEqual(self.procedure_file.name, "renamed.docx")

    def test_a_version_is_locked_once_a_new_one_is_shown(self):
        self.assertFalse(self.version.editables_locked)
        self.page.with_user(self.editor).write({"content": "<p>Version two</p>"})
        self.assertTrue(self.version.editables_locked)

    def test_new_version_made_from_the_screens_copies_whole_files(self):
        # The web client reads binary fields as their sizes
        self.page.with_user(self.editor).with_context(bin_size=True).write(
            {"content": "<p>Version two</p>"}
        )
        copied = self.env[EDITABLE_FILE].search(
            [
                ("history_id", "=", self.page.history_head.id),
                ("name", "=", "procedure.docx"),
            ]
        )
        self.assertEqual(base64.b64decode(copied.file), b"Word source of the procedure")

    def test_duplicated_version_made_from_the_screens_keeps_whole_files(self):
        duplicate = (
            self.version.with_user(self.editor).with_context(bin_size=True).copy()
        )
        copied = self.env[EDITABLE_FILE].search(
            [("history_id", "=", duplicate.id), ("name", "=", "procedure.docx")]
        )
        self.assertEqual(base64.b64decode(copied.file), b"Word source of the procedure")

    def test_writer_who_is_not_an_editor_duplicates_a_version_with_its_files(self):
        writers = self.env["res.groups"].create({"name": "Document writers test"})
        self.env["ir.model.access"].create(
            {
                "name": "document.page.history writer test",
                "model_id": self.env["ir.model"]._get("document.page.history").id,
                "group_id": writers.id,
                "perm_read": True,
                "perm_create": True,
            }
        )
        self.reader.groups_id = [(4, writers.id)]
        duplicate = self.version.with_user(self.reader).copy()
        self.assertEqual(
            self.env[EDITABLE_FILE]
            .search([("history_id", "=", duplicate.id)])
            .mapped("name"),
            ["procedure.docx", "annex.xlsx"],
        )

    def test_document_deleter_who_is_not_an_editor_deletes_a_document(self):
        # The right to delete documents, given in the database to a group of its own
        deleters = self.env["res.groups"].create({"name": "Document deleters test"})
        self.env["ir.model.access"].create(
            {
                "name": "document.page deleter test",
                "model_id": self.env["ir.model"]._get("document.page").id,
                "group_id": deleters.id,
                "perm_read": True,
                "perm_unlink": True,
            }
        )
        groups = deleters
        groups += self.env.ref("base.group_user")
        deleter = self._new_user("document_deleter_test", groups, self.env.company)
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        self.page.with_user(deleter).unlink()
        self.assertFalse(self.page.exists())
        self.assertFalse(attachments.exists())

    def test_files_stay_when_odoo_refuses_a_document_deletion_after_its_checks(self):
        attachments = self._attachment_of(self.procedure_file)
        attachments += self._attachment_of(self.annex_file)
        self.assertEqual(len(attachments), 2)
        # A client that read the document before its last change
        stale = {
            "__last_update": {"document.page,%d" % self.page.id: "2000-01-01 00:00:00"}
        }
        with self.assertRaises(ValidationError) as error:
            self.page.with_context(**stale).unlink()
        self.assertEqual(
            str(error.exception), CONCURRENCY_REFUSAL % ("Document Page", self.page.id)
        )
        self.assertTrue(self.procedure_file.exists())
        self.assertTrue(self.annex_file.exists())
        self.assertEqual(attachments.exists(), attachments)

    def test_system_administrator_editor_writes_other_attachments(self):
        groups = self.env.ref("base.group_system")
        groups += self.env.ref("document_page.group_document_editor")
        administrator = self._new_user(
            "administrator_editor_test", groups, self.env.company
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": "notes.txt",
                "res_model": "document.page",
                "res_id": self.page.id,
                "datas": encoded("Notes of the document"),
            }
        )
        attachment.with_user(administrator).write({"datas": encoded("New notes")})
        attachment.invalidate_cache()
        self.assertEqual(base64.b64decode(attachment.datas), b"New notes")

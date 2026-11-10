# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocumentPageExtension(TransactionCase):
    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        group_user = self.env.ref("base.group_user")
        group_system = self.env.ref("base.group_system")
        group_reader = self.env.ref("knowledge.group_document_user")
        group_editor = self.env.ref("document_page.group_document_editor")
        group_manager = self.env.ref("document_page.group_document_manager")
        # With an email, as the users of the tests of Odoo: Odoo posts no message
        # without the email of its author
        users = self.env["res.users"].with_context(no_reset_password=True)
        self.reader = users.create(
            {
                "name": "Reader",
                "login": "reader_dpe_test",
                "email": "reader_dpe_test@example.com",
                "groups_id": [(6, 0, [group_reader.id])],
            }
        )
        self.editor = users.create(
            {
                "name": "Editor",
                "login": "editor_dpe_test",
                "email": "editor_dpe_test@example.com",
                "groups_id": [(6, 0, [group_editor.id])],
            }
        )
        # An internal user with no role in Knowledge, who cannot read the pages
        self.outsider = users.create(
            {
                "name": "Outsider",
                "login": "outsider_dpe_test",
                "email": "outsider_dpe_test@example.com",
                "groups_id": [(6, 0, [group_user.id])],
            }
        )
        self.administrator = users.create(
            {
                "name": "Administrator",
                "login": "administrator_dpe_test",
                "email": "administrator_dpe_test@example.com",
                "groups_id": [(6, 0, [group_system.id, group_manager.id])],
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
            }
        )

    def _upload(self, user, res_model, res_id=False):
        # What the editor does when the user inserts a file: an attachment of the
        # record of the form, of no record while the form is not saved, with an
        # access token for its link
        attachment = (
            self.env["ir.attachment"]
            .with_user(user)
            .create(
                {
                    "name": "annex.pdf",
                    "datas": base64.b64encode(b"PDF file"),
                    "res_model": res_model,
                    "res_id": res_id,
                }
            )
        )
        attachment.generate_access_token()
        return attachment.with_env(self.env)

    def _download(self, user, attachment):
        # What the link of the file gets. As in the tests of Odoo, the cache, filled
        # as superuser, is emptied first, so that the access of the user is checked
        attachment.flush()
        attachment.invalidate_cache()
        status, _headers, _content = (
            self.env["ir.http"]
            .with_user(user)
            .binary_content(id=attachment.id, access_token=attachment.access_token)
        )
        return status

    def test_reader_downloads_a_file_of_the_page(self):
        upload = self._upload(self.editor, "document.page", self.page.id)
        self.assertEqual(self._download(self.reader, upload), 200)

    def test_outsider_cannot_download_a_file_of_the_page(self):
        # With the access token of the link all the same, which alone opens the file
        # to anyone. The link answers "Not found" to this 403
        upload = self._upload(self.editor, "document.page", self.page.id)
        self.assertEqual(self._download(self.outsider, upload), 403)

    def test_outsider_is_refused_by_the_check_of_web_content(self):
        # The routes that check a file as /web/content does call this method
        # directly, without binary_content: they refuse the file too, with the
        # access token of its link all the same
        upload = self._upload(self.editor, "document.page", self.page.id)
        record, status = (
            self.env["ir.http"]
            .with_user(self.outsider)
            ._get_record_and_check(
                model="ir.attachment", id=upload.id, access_token=upload.access_token
            )
        )
        self.assertEqual((record, status), (None, 403))

    def test_uploader_downloads_a_file_of_a_page_not_saved_yet(self):
        upload = self._upload(self.editor, "document.page")
        self.assertEqual(self._download(self.editor, upload), 200)

    def test_reader_cannot_download_a_file_of_a_page_not_saved_yet(self):
        upload = self._upload(self.editor, "document.page")
        self.assertEqual(self._download(self.reader, upload), 403)

    def test_administrator_downloads_a_file_of_a_page_not_saved_yet(self):
        upload = self._upload(self.editor, "document.page")
        self.assertEqual(self._download(self.administrator, upload), 200)

    def test_file_of_another_model_is_left_to_odoo(self):
        # Its access token opens it to anyone, as Odoo does with any file
        partner = self.env["res.partner"].create({"name": "Supplier"})
        attachment = self.env["ir.attachment"].create(
            {
                "name": "contract.pdf",
                "datas": base64.b64encode(b"PDF file"),
                "res_model": "res.partner",
                "res_id": partner.id,
            }
        )
        attachment.generate_access_token()
        self.assertEqual(self._download(self.outsider, attachment), 200)

    def test_reader_downloads_a_file_of_a_version(self):
        upload = self._upload(
            self.editor, "document.page.history", self.page.history_head.id
        )
        self.assertEqual(self._download(self.reader, upload), 200)

    def test_outsider_cannot_download_a_file_of_a_version(self):
        upload = self._upload(
            self.editor, "document.page.history", self.page.history_head.id
        )
        self.assertEqual(self._download(self.outsider, upload), 403)

    def test_file_inserted_in_a_new_version_becomes_a_file_of_the_version(self):
        upload = self._upload(self.editor, "document.page.history")
        version = (
            self.env["document.page.history"]
            .with_user(self.editor)
            .create(
                {
                    "page_id": self.page.id,
                    "content": '<p><a href="/web/content/%d?download=true">'
                    "annex.pdf</a></p>" % upload.id,
                }
            )
        )
        self.assertEqual(upload.res_id, version.id)

    def test_file_inserted_by_another_user_is_left_as_it_is(self):
        upload = self._upload(self.administrator, "document.page.history")
        self.env["document.page.history"].with_user(self.editor).create(
            {
                "page_id": self.page.id,
                "content": '<p><a href="/web/content/%d?download=true">'
                "annex.pdf</a></p>" % upload.id,
            }
        )
        self.assertFalse(upload.res_id)

    def test_administrator_saves_a_file_inserted_by_another_user(self):
        upload = self._upload(self.editor, "document.page.history")
        version = (
            self.env["document.page.history"]
            .with_user(self.administrator)
            .create(
                {
                    "page_id": self.page.id,
                    "content": '<p><a href="/web/content/%d?download=true">'
                    "annex.pdf</a></p>" % upload.id,
                }
            )
        )
        self.assertEqual(upload.res_id, version.id)

    def test_file_linked_when_editing_a_version_becomes_a_file_of_the_version(self):
        version = self.page.history_head
        upload = self._upload(self.editor, "document.page.history")
        version.with_user(self.editor).write(
            {
                "content": '<p><a href="/web/content/%d?download=true">'
                "annex.pdf</a></p>" % upload.id,
            }
        )
        self.assertEqual(upload.res_id, version.id)

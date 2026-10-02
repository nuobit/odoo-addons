# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrAttachmentContentFiles(TransactionCase):
    """The guard of ``ir.attachment``: a file saved in the content of a
    ``document.page`` cannot be deleted, attached to another record or changed
    while the page exists, except by a system administrator; the page image,
    the chatter files, unrelated attachments and the page's own cascade delete
    are left untouched.
    """

    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        self.Attachment = self.env["ir.attachment"]
        self.category = self.DocumentPage.create({"name": "Cat", "type": "category"})
        self.page = self.DocumentPage.create(
            {"name": "Page", "type": "content", "parent_id": self.category.id}
        )
        self.attachment = self.Attachment.create(
            {
                "name": "embedded.txt",
                "res_model": "document.page",
                "res_id": self.page.id,
                "datas": base64.b64encode(b"content"),
                "mimetype": "text/plain",
            }
        )
        self.editor = self.env["res.users"].create(
            {
                "name": "Doc Editor",
                "login": "doceditor_unlink_test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("document_page.group_document_editor").id,
                        ],
                    )
                ],
            }
        )
        self.administrator = self.env["res.users"].create(
            {
                "name": "Doc Administrator",
                "login": "docadmin_unlink_test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("base.group_system").id,
                            self.env.ref("document_page.group_document_editor").id,
                        ],
                    )
                ],
            }
        )

    def _content_file(self):
        content_file = self.Attachment.create(
            {
                "name": "annex.txt",
                "res_model": "document.page",
                "res_id": self.page.id,
                "datas": base64.b64encode(b"annex"),
                "mimetype": "text/plain",
            }
        )
        self.page.with_user(self.editor).write(
            {
                "content": '<p><a href="/web/content/%d?download=true">annex</a></p>'
                % content_file.id
            }
        )
        return content_file

    def test_attachment_box_file_can_be_deleted(self):
        self.attachment.with_user(self.editor).unlink()
        self.assertFalse(self.attachment.exists())

    def test_unlink_allowed_when_not_linked(self):
        free = self.Attachment.with_user(self.editor).create(
            {
                "name": "free.txt",
                "datas": base64.b64encode(b"x"),
                "mimetype": "text/plain",
            }
        )
        free.unlink()
        self.assertFalse(free.exists())

    def test_unlink_allowed_when_page_missing(self):
        # res_id pointing to a non-existing page does not block the deletion.
        content_file = self._content_file()
        content_file.res_id = self.page.id + 100000
        content_file.with_user(self.editor).unlink()
        self.assertFalse(content_file.exists())

    def test_manager_deletes_a_page_with_its_content_files(self):
        manager = self.env["res.users"].create(
            {
                "name": "Doc Manager",
                "login": "docmanager_unlink_test",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("document_page.group_document_manager").id,
                        ],
                    )
                ],
            }
        )
        content_file = self._content_file()
        self.page.with_user(manager).unlink()
        self.assertFalse(self.page.exists())
        self.assertFalse(content_file.exists())

    def test_cleared_page_image_is_deleted(self):
        self.page.with_user(self.editor).write({"image": base64.b64encode(b"image")})
        image = self.Attachment.search(
            [
                ("res_model", "=", "document.page"),
                ("res_id", "=", self.page.id),
                ("res_field", "=", "image"),
            ]
        )
        self.assertEqual(len(image), 1)
        self.page.with_user(self.editor).write({"image": False})
        self.assertFalse(image.exists())

    def test_chatter_message_file_can_be_deleted(self):
        attachment = self.Attachment.create(
            {
                "name": "minutes.txt",
                "res_model": "mail.compose.message",
                "res_id": 0,
                "datas": base64.b64encode(b"minutes"),
                "mimetype": "text/plain",
            }
        )
        self.page.message_post(body="Minutes", attachment_ids=[attachment.id])
        self.assertEqual(attachment.res_model, "document.page")
        attachment.with_user(self.editor).unlink()
        self.assertFalse(attachment.exists())

    def test_content_file_kept_after_its_link_is_removed(self):
        page = self.DocumentPage.create(
            {
                "name": "Procedure With Annex",
                "type": "content",
                "parent_id": self.category.id,
            }
        )
        annex = self.Attachment.with_user(self.editor).create(
            {
                "name": "annex-1.txt",
                "res_model": "document.page",
                "res_id": page.id,
                "datas": base64.b64encode(b"annex 1"),
                "mimetype": "text/plain",
            }
        )
        page.with_user(self.editor).write(
            {
                "content": '<p><a href="/web/content/%d?download=true">Annex 1</a></p>'
                % annex.id
            }
        )
        page.with_user(self.editor).write({"content": "<p>Annex 1 withdrawn</p>"})
        with self.assertRaises(UserError) as error:
            annex.unlink()
        self.assertIn("Procedure With Annex", str(error.exception))
        self.assertTrue(annex.exists())

    def test_administrator_deletes_a_content_file(self):
        content_file = self._content_file()
        content_file.with_user(self.administrator).unlink()
        self.assertFalse(content_file.exists())

    def test_file_uploaded_into_a_new_page_is_kept(self):
        # An image link: a module that tracks the download links of a version
        # anchors a linked file itself, which would hide this anchoring.
        upload = self.Attachment.with_user(self.editor).create(
            {
                "name": "figure.txt",
                "res_model": "document.page",
                "res_id": 0,
                "datas": base64.b64encode(b"figure"),
                "mimetype": "text/plain",
            }
        )
        page = self.DocumentPage.with_user(self.editor).create(
            {
                "name": "New Procedure",
                "type": "content",
                "parent_id": self.category.id,
                "content": '<p><img src="/web/image/%d"/></p>' % upload.id,
            }
        )
        page.write({"content": "<p>Figure withdrawn</p>"})
        with self.assertRaises(UserError) as error:
            upload.unlink()
        self.assertIn("- New Procedure: figure.txt", str(error.exception))
        self.assertTrue(upload.exists())

    def test_unlink_of_several_files_refused_when_one_is_kept(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            (content_file + self.attachment).with_user(self.editor).unlink()
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertNotIn("embedded.txt", str(error.exception))
        self.assertTrue(content_file.exists())
        self.assertTrue(self.attachment.exists())

    def test_saving_again_leaves_the_content_files_untouched(self):
        content_file = self._content_file()
        self.page.with_user(self.administrator).write(
            {
                "content": '<p><a href="/web/content/%d?download=true">annex</a> '
                "reviewed</p>" % content_file.id
            }
        )
        self.assertEqual(content_file.write_uid, self.editor)

    def test_editor_cannot_unmark_a_content_file(self):
        content_file = self._content_file()
        with self.assertRaises(AccessError):
            content_file.with_user(self.editor).write(
                {"document_page_content_file": False}
            )
        self.assertTrue(content_file.document_page_content_file)

    def test_editor_cannot_attach_a_content_file_to_another_record(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write({"res_id": self.category.id})
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.res_id, self.page.id)

    def test_editor_cannot_attach_a_content_file_to_another_model(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write({"res_model": "res.partner"})
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.res_model, "document.page")

    def test_editor_cannot_attach_a_content_file_to_a_field(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write({"res_field": "image"})
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertFalse(content_file.res_field)

    def test_editor_cannot_replace_a_content_file(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write(
                {"datas": base64.b64encode(b"another annex")}
            )
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.raw, b"annex")

    def test_editor_cannot_empty_a_content_file(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write({"raw": b""})
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.raw, b"annex")

    def test_editor_cannot_overwrite_the_stored_bytes_of_a_content_file(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write({"db_datas": b"another annex"})
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.raw, b"annex")

    def test_editor_cannot_turn_a_content_file_into_a_link(self):
        content_file = self._content_file()
        with self.assertRaises(UserError) as error:
            content_file.with_user(self.editor).write(
                {"type": "url", "url": "https://example.com/annex.txt"}
            )
        self.assertIn("- Page: annex.txt", str(error.exception))
        self.assertEqual(content_file.type, "binary")

    def test_administrator_attaches_a_content_file_to_another_record(self):
        content_file = self._content_file()
        content_file.with_user(self.administrator).write({"res_id": self.category.id})
        self.assertEqual(content_file.res_id, self.category.id)

    def test_editor_shares_a_content_file_with_an_access_token(self):
        content_file = self._content_file()
        content_file.with_user(self.editor).generate_access_token()
        self.assertTrue(content_file.access_token)

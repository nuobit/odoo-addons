# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrAttachmentUnlink(TransactionCase):
    """The ``ir.attachment.unlink`` guard: a file linked to a ``document.page``
    (``res_model``/``res_id``) cannot be deleted, while unrelated attachments
    and the page's own cascade delete are left untouched.
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

    def _free_attachment(self):
        return self.Attachment.create(
            {
                "name": "free.txt",
                "datas": base64.b64encode(b"x"),
                "mimetype": "text/plain",
            }
        )

    def test_unlink_blocked_when_linked_to_page(self):
        with self.assertRaises(UserError):
            self.attachment.unlink()
        self.assertTrue(self.attachment.exists())

    def test_unlink_allowed_when_not_linked(self):
        free = self._free_attachment()
        free.unlink()
        self.assertFalse(free.exists())

    def test_unlink_allowed_when_page_missing(self):
        # res_id pointing to a non-existing page does not block the deletion.
        self.attachment.res_id = self.page.id + 100000
        self.attachment.unlink()
        self.assertFalse(self.attachment.exists())

    def test_delete_page_cascades_without_blocking(self):
        page_id = self.page.id
        attachment_id = self.attachment.id
        self.page.unlink()
        self.assertFalse(self.DocumentPage.browse(page_id).exists())
        # The cascade removed the linked attachment; the guard did not block it.
        self.assertFalse(self.Attachment.browse(attachment_id).exists())

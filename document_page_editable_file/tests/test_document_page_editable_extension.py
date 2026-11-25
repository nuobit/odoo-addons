# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase, tagged

EDITABLE_FILE = "document.page.editable.file"


@tagged("post_install", "-at_install")
class TestDocumentPageEditableExtension(SavepointCase):
    """A module that adds a field to the editable files keeps it on every copy."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)
        from .fake_models import DocumentPageEditableFile

        cls.loader.update_registry((DocumentPageEditableFile,))
        cls.page = cls.env["document.page"].create(
            {
                "name": "Procedure",
                "type": "content",
                "draft_name": "1.0",
                "draft_summary": "First version",
                "content": "<p>Version one</p>",
            }
        )
        cls.procedure_file = cls.env[EDITABLE_FILE].create(
            {
                "history_id": cls.page.history_head.id,
                "name": "procedure.docx",
                "file": base64.b64encode(b"Word source of the procedure"),
                "revision": "Rev. 3",
            }
        )

    def test_new_version_copies_a_field_another_module_adds(self):
        self.page.write({"content": "<p>Version two</p>"})
        self.assertNotEqual(self.page.history_head, self.procedure_file.history_id)
        self.assertEqual(
            self.page.history_head.editable_file_ids.mapped("revision"), ["Rev. 3"]
        )

    def test_duplicated_version_copies_a_field_another_module_adds(self):
        duplicate = self.procedure_file.history_id.copy()
        self.assertEqual(duplicate.editable_file_ids.mapped("revision"), ["Rev. 3"])

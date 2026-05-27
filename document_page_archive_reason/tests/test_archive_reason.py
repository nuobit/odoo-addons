# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestArchiveReason(TransactionCase):
    def setUp(self):
        super().setUp()
        self.DocumentPage = self.env["document.page"]
        self.Wizard = self.env["document.page.archive.reason"]
        self.category = self.DocumentPage.create(
            {"name": "Test Category", "type": "category"}
        )

    def _create_page(self, **vals):
        defaults = {
            "name": "Test Page",
            "type": "content",
            "parent_id": self.category.id,
        }
        defaults.update(vals)
        return self.DocumentPage.create(defaults)

    def test_action_archive_opens_wizard(self):
        page = self._create_page()
        action = page.action_archive()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "document.page.archive.reason")
        self.assertEqual(action["target"], "new")
        self.assertTrue(
            page.active,
            "Document must remain active until the wizard confirms.",
        )

    def test_action_unarchive_archives_directly(self):
        page = self._create_page()
        page.with_context(archive_reason_provided=True).action_archive()
        self.assertFalse(page.active)
        page.action_unarchive()
        self.assertTrue(
            page.active,
            "Unarchive must reactivate directly, without opening the wizard.",
        )

    def test_wizard_confirm_archives_and_posts_message(self):
        page = self._create_page()
        count_before = len(page.message_ids)
        wizard = self.Wizard.create(
            {
                "document_page_ids": [(6, 0, [page.id])],
                "reason": "Replaced by procedure P-016",
            }
        )
        wizard.action_confirm()
        self.assertFalse(page.active)
        self.assertEqual(len(page.message_ids), count_before + 1)
        self.assertIn("archived", page.message_ids[0].body)
        self.assertIn("Replaced by procedure P-016", page.message_ids[0].body)

    def test_archive_reason_provided_context_bypasses_wizard(self):
        page = self._create_page()
        page.with_context(archive_reason_provided=True).action_archive()
        self.assertFalse(
            page.active,
            "With archive_reason_provided=True the wizard must be bypassed "
            "and the document archived directly.",
        )

    def test_mixed_selection_archive_raises(self):
        active_page = self._create_page(name="Still active")
        archived_page = self._create_page(name="Already archived")
        archived_page.with_context(archive_reason_provided=True).action_archive()
        records = active_page + archived_page
        with self.assertRaises(UserError) as ctx:
            records.action_archive()
        self.assertIn("already archived", str(ctx.exception))
        self.assertIn(archived_page.display_name, str(ctx.exception))

    def test_archive_all_already_archived_raises(self):
        page = self._create_page()
        page.with_context(archive_reason_provided=True).action_archive()
        with self.assertRaises(UserError) as ctx:
            page.action_archive()
        self.assertIn("already archived", str(ctx.exception))

    def test_mixed_selection_unarchive_raises(self):
        active_page = self._create_page(name="Active page")
        archived_page = self._create_page(name="To unarchive")
        archived_page.with_context(archive_reason_provided=True).action_archive()
        records = active_page + archived_page
        with self.assertRaises(UserError) as ctx:
            records.action_unarchive()
        self.assertIn("already active", str(ctx.exception))
        self.assertIn(active_page.display_name, str(ctx.exception))

    def test_unarchive_all_already_active_raises(self):
        page = self._create_page()
        with self.assertRaises(UserError) as ctx:
            page.action_unarchive()
        self.assertIn("already active", str(ctx.exception))

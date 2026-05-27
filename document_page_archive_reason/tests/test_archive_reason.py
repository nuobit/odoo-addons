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

    def _archive_with_reason(self, pages, reason="Replaced by procedure P-016"):
        """Archive pages through the natural wizard workflow."""
        wizard = self.Wizard.create(
            {
                "document_page_ids": [(6, 0, pages.ids)],
                "reason": reason,
            }
        )
        wizard.action_confirm()
        return wizard

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

    def test_wizard_confirm_archives_stores_reason_and_posts_message(self):
        page = self._create_page()
        count_before = len(page.message_ids)
        self._archive_with_reason(page, reason="Replaced by procedure P-016")
        self.assertFalse(page.active)
        self.assertEqual(page.archive_reason, "Replaced by procedure P-016")
        self.assertEqual(len(page.message_ids), count_before + 1)
        self.assertIn("archived", page.message_ids[0].body)
        self.assertIn("Replaced by procedure P-016", page.message_ids[0].body)

    def test_wizard_requires_non_empty_reason(self):
        page = self._create_page()
        wizard = self.Wizard.create(
            {"document_page_ids": [(6, 0, page.ids)], "reason": "   "}
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()
        self.assertTrue(page.active, "Page must stay active when reason is empty.")

    def test_wizard_escapes_reason_in_chatter(self):
        page = self._create_page()
        self._archive_with_reason(page, reason="<b>boom</b>")
        body = page.message_ids[0].body
        self.assertIn("boom", body)
        self.assertNotIn("<b>boom</b>", body)

    def test_unarchive_is_direct_and_clears_reason(self):
        page = self._create_page()
        self._archive_with_reason(page)
        self.assertFalse(page.active)
        self.assertTrue(page.archive_reason)
        page.action_unarchive()
        self.assertTrue(
            page.active,
            "Unarchive must reactivate directly, without opening the wizard.",
        )
        self.assertFalse(
            page.archive_reason,
            "Unarchiving must clear the stored archive reason.",
        )

    def test_unarchive_ignores_already_active(self):
        # Standard Odoo behavior: unarchiving active records is a no-op,
        # not an error (no reason is applied on unarchive).
        active_page = self._create_page(name="Active page")
        archived_page = self._create_page(name="To unarchive")
        self._archive_with_reason(archived_page)
        records = active_page + archived_page
        records.action_unarchive()
        self.assertTrue(active_page.active)
        self.assertTrue(archived_page.active)

    def test_mixed_selection_archive_raises(self):
        active_page = self._create_page(name="Still active")
        archived_page = self._create_page(name="Already archived")
        self._archive_with_reason(archived_page)
        records = active_page + archived_page
        with self.assertRaises(UserError) as ctx:
            records.action_archive()
        self.assertIn("already archived", str(ctx.exception))
        self.assertIn(archived_page.display_name, str(ctx.exception))

    def test_archive_all_already_archived_raises(self):
        page = self._create_page()
        self._archive_with_reason(page)
        with self.assertRaises(UserError) as ctx:
            page.action_archive()
        self.assertIn("already archived", str(ctx.exception))

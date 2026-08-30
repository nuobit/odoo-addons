# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestReviewCopyLines(TransactionCase):
    def setUp(self):
        super().setUp()
        self.review = self.env["mgmtsystem.review"].create(
            {
                "name": "Template review",
                "date": "2026-06-12 10:00:00",
                "line_ids": [
                    (0, 0, {"name": "Change description"}),
                    (0, 0, {"name": "Change reason", "decision": "Pending"}),
                    (0, 0, {"name": "Linked action", "type": "action"}),
                ],
            }
        )

    def test_copy_includes_lines(self):
        copy = self.review.copy()
        self.assertEqual(len(copy.line_ids), 3)
        for field in ("name", "type", "decision"):
            self.assertEqual(
                copy.line_ids.mapped(field),
                self.review.line_ids.mapped(field),
            )
        self.assertFalse(
            set(copy.line_ids.ids) & set(self.review.line_ids.ids),
            "Copied lines must be new records, not shared with the source.",
        )
        self.assertEqual(
            len(self.review.line_ids),
            3,
            "The source review must keep its own lines.",
        )

    def test_copy_starts_open(self):
        self.review.button_close()
        self.assertEqual(self.review.state, "done")
        copy = self.review.copy()
        self.assertEqual(
            copy.state,
            "open",
            "A duplicate must start open even if the source is closed.",
        )
        self.assertEqual(
            self.review.state,
            "done",
            "Duplicating must not alter the source review.",
        )
        copy.button_close()
        self.assertEqual(
            copy.state,
            "done",
            "The copy must be able to go through its own lifecycle.",
        )

    def test_copy_gets_new_reference(self):
        copy = self.review.copy()
        self.assertTrue(copy.reference)
        self.assertNotEqual(copy.reference, self.review.reference)

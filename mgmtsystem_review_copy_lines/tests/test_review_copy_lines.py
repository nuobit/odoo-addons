# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestReviewCopyLines(TransactionCase):
    def setUp(self):
        super().setUp()
        self.action = self.env["mgmtsystem.action"].create(
            {"name": "Linked action", "type_action": "immediate"}
        )
        partner = self.env["res.partner"].create({"name": "Nonconformity partner"})
        origin = self.env["mgmtsystem.nonconformity.origin"].create(
            {"name": "Nonconformity origin"}
        )
        self.nonconformity = self.env["mgmtsystem.nonconformity"].create(
            {
                "partner_id": partner.id,
                "manager_user_id": self.env.user.id,
                "responsible_user_id": self.env.user.id,
                "origin_ids": [(6, 0, origin.ids)],
                "description": "Linked nonconformity",
            }
        )
        self.review = self.env["mgmtsystem.review"].create(
            {
                "name": "Template review",
                "date": "2026-06-12 10:00:00",
                "line_ids": [
                    (0, 0, {"name": "Change description"}),
                    (0, 0, {"name": "Change reason", "decision": "Pending"}),
                    (
                        0,
                        0,
                        {
                            "name": "Linked action",
                            "type": "action",
                            "action_id": self.action.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Linked nonconformity",
                            "type": "nonconformity",
                            "nonconformity_id": self.nonconformity.id,
                        },
                    ),
                ],
            }
        )

    def test_copy_includes_lines(self):
        copy = self.review.copy()
        self.assertEqual(len(copy.line_ids), 4)
        self.assertEqual(
            copy.line_ids.mapped("name"),
            [
                "Change description",
                "Change reason",
                "Linked action",
                "Linked nonconformity",
            ],
        )
        self.assertEqual(
            copy.line_ids.mapped("type"), [False, False, "action", "nonconformity"]
        )
        self.assertEqual(
            copy.line_ids.mapped("decision"), [False, "Pending", False, False]
        )
        self.assertFalse(
            copy.line_ids & self.review.line_ids,
            "Copied lines must be new records, not shared with the source.",
        )
        self.assertEqual(
            len(self.review.line_ids),
            4,
            "The source review must keep its own lines.",
        )

    def test_copy_keeps_linked_records(self):
        copy = self.review.copy()
        self.assertEqual(copy.line_ids[2].action_id, self.action)
        self.assertEqual(copy.line_ids[3].nonconformity_id, self.nonconformity)

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

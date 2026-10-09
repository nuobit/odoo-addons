# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.tests import HttpCase, tagged

from .common import TestProjectTaskRestrictedCommon


@tagged("post_install", "-at_install")
class TestChatterPost(TestProjectTaskRestrictedCommon, HttpCase):
    def test_mention_in_note_reaches_non_member(self):
        self.authenticate("member_test", "member_test")
        # the chatter's composer posts with mail_post_autofollow
        response = self.url_open(
            "/mail/message/post",
            data=json.dumps(
                {
                    "params": {
                        "thread_model": "project.task",
                        "thread_id": self.task_restricted.id,
                        "post_data": {
                            "body": "Hourly rate agreed with the customer",
                            "message_type": "comment",
                            "subtype_xmlid": "mail.mt_note",
                            "partner_ids": [self.user_developer.partner_id.id],
                        },
                        "context": {"mail_post_autofollow": True},
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        message = self.env["mail.message"].browse(response.json()["result"]["id"])
        self.assertEqual(message.partner_ids, self.user_developer.partner_id)
        self.assertEqual(
            [
                (notification.res_partner_id, notification.notification_type)
                for notification in message.notification_ids
            ],
            [(self.user_developer.partner_id, "email")],
        )
        self.assertEqual(
            self.task_restricted.message_partner_ids, self.user_member.partner_id
        )

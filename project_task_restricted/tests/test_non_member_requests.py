# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.tests import HttpCase, tagged

from .common import TestProjectTaskRestrictedCommon


# a request starts with an empty cache, unlike the users of a test transaction
@tagged("post_install", "-at_install")
class TestNonMemberRequests(TestProjectTaskRestrictedCommon, HttpCase):
    def test_non_member_reassigns_unrestricted_task(self):
        self.authenticate("developer_test", "developer_test")
        response = self.url_open(
            "/web/dataset/call_kw/project.task/write",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {
                        "model": "project.task",
                        "method": "write",
                        "args": [
                            self.task_quote.ids,
                            {"user_ids": [[4, self.user_developer.id]]},
                        ],
                        "kwargs": {},
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.json(), {"jsonrpc": "2.0", "id": 1, "result": True})
        # the request wrote through another environment
        self.task_quote.invalidate_cache()
        self.assertEqual(
            set(self.task_quote.user_ids.ids),
            {self.user_member.id, self.user_developer.id},
        )

    def test_non_member_follows_unrestricted_task(self):
        self.authenticate("developer_test", "developer_test")
        response = self.url_open(
            "/web/dataset/call_kw/project.task/message_subscribe",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {
                        "model": "project.task",
                        "method": "message_subscribe",
                        "args": [self.task_quote.ids],
                        "kwargs": {"partner_ids": self.user_developer.partner_id.ids},
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.json(), {"jsonrpc": "2.0", "id": 1, "result": True})
        # the request wrote through another environment
        self.task_quote.invalidate_cache()
        self.assertEqual(
            set(self.task_quote.message_partner_ids.ids),
            {self.user_member.partner_id.id, self.user_developer.partner_id.id},
        )

    # a copy reads every copied field as the user, the protected one included
    def test_non_member_duplicates_unrestricted_task(self):
        self.authenticate("developer_test", "developer_test")
        response = self.url_open(
            "/web/dataset/call_kw/project.task/copy",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {
                        "model": "project.task",
                        "method": "copy",
                        "args": [self.task_quote.ids],
                        "kwargs": {},
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        task = self.env["project.task"].browse(response.json()["result"])
        self.assertEqual(task.name, "Pigs Quote (copy)")

    def test_non_member_administrator_duplicates_project(self):
        self.authenticate("administrator_test", "administrator_test")
        response = self.url_open(
            "/web/dataset/call_kw/project.project/copy",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {
                        "model": "project.project",
                        "method": "copy",
                        "args": [self.project_pigs.ids],
                        "kwargs": {},
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        project = self.env["project.project"].browse(response.json()["result"])
        self.assertEqual(
            sorted(project.task_ids.mapped("name")),
            ["Pigs ManagerTask", "Pigs Quote", "Pigs UserTask"],
        )

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from .common import TestProjectTaskRestrictedCommon


# the project portal reads tasks as superuser as soon as the address carries a
# token, even one it never checks against the project
@tagged("post_install", "-at_install")
class TestPortal(TestProjectTaskRestrictedCommon, HttpCase):
    def test_project_page_with_any_token_lists_no_restricted_task(self):
        self.authenticate("developer_test", "developer_test")
        response = self.url_open(
            "/my/project/%s?access_token=anything" % self.project_pigs.id
        )
        self.assertIn("Pigs Quote", response.text)
        self.assertNotIn("Pigs Budget", response.text)

    def test_project_page_with_project_token_lists_no_restricted_task(self):
        token = self.project_pigs._portal_ensure_token()
        response = self.url_open(
            "/my/project/%s?access_token=%s" % (self.project_pigs.id, token)
        )
        self.assertIn("Pigs Quote", response.text)
        self.assertNotIn("Pigs Budget", response.text)

    def test_project_page_lists_restricted_task_to_member(self):
        self.authenticate("member_test", "member_test")
        response = self.url_open(
            "/my/project/%s?access_token=anything" % self.project_pigs.id
        )
        self.assertIn("Pigs Budget", response.text)

    def test_project_task_page_with_any_token_refuses_restricted_task(self):
        self.task_restricted.sudo().description = "Internal price 4500"
        self.authenticate("developer_test", "developer_test")
        response = self.url_open(
            "/my/project/%s/task/%s?access_token=anything"
            % (self.project_pigs.id, self.task_restricted.id)
        )
        self.assertNotIn("Internal price 4500", response.text)
        self.assertTrue(response.url.endswith("/my"))

    def test_project_task_page_shows_restricted_task_to_member(self):
        self.task_restricted.sudo().description = "Internal price 4500"
        self.authenticate("member_test", "member_test")
        response = self.url_open(
            "/my/project/%s/task/%s?access_token=anything"
            % (self.project_pigs.id, self.task_restricted.id)
        )
        self.assertIn("Internal price 4500", response.text)

    def test_marking_voids_task_token(self):
        token = self.task_quote._portal_ensure_token()
        self.task_quote.sudo().description = "Internal price 4500"
        self.task_quote.with_user(self.user_member).restricted = True
        self.assertFalse(self.task_quote.access_token)
        response = self.url_open(
            "/my/task/%s?access_token=%s" % (self.task_quote.id, token)
        )
        self.assertNotIn("Internal price 4500", response.text)

    def test_project_token_opens_no_restricted_task(self):
        self.task_restricted.sudo().description = "Internal price 4500"
        token = self.project_pigs._portal_ensure_token()
        response = self.url_open(
            "/my/project/%s/task/%s?access_token=%s"
            % (self.project_pigs.id, self.task_restricted.id, token)
        )
        self.assertNotIn("Internal price 4500", response.text)
        self.assertTrue(response.history[0].headers["Location"].endswith("/my"))

    def test_old_token_fetches_no_restricted_task_message(self):
        token = self.task_quote._portal_ensure_token()
        self.task_quote.with_user(self.user_member).message_post(
            body="Internal price 4500",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.task_quote.with_user(self.user_member).restricted = True
        # Odoo answers an error: it compares the token with none
        with mute_logger("odoo.http"):
            response = self.url_open(
                "/mail/chatter_fetch",
                data=json.dumps(
                    {
                        "params": {
                            "res_model": "project.task",
                            "res_id": self.task_quote.id,
                            "token": token,
                        }
                    }
                ),
                headers={"Content-Type": "application/json"},
            )
        self.assertNotIn("Internal price 4500", response.text)

    # Odoo signs a portal post over the record's token, and no marked task has
    # one: a signature made over an empty token must not post on it
    def test_signature_over_empty_token_posts_nothing_on_restricted_task(self):
        self.task_quote.sudo().access_token = False
        partner = self.user_member.partner_id
        signature = self.task_quote.sudo()._sign_token(partner.id)
        # Odoo answers a refusal
        with mute_logger("odoo.http"):
            self.url_open(
                "/mail/chatter_post",
                data=json.dumps(
                    {
                        "params": {
                            "res_model": "project.task",
                            "res_id": self.task_restricted.id,
                            "message": "Forged note",
                            "hash": signature,
                            "pid": partner.id,
                        }
                    }
                ),
                headers={"Content-Type": "application/json"},
            )
        self.task_restricted.invalidate_cache(["message_ids"])
        self.assertFalse(
            self.task_restricted.sudo().message_ids.filtered(
                lambda message: "Forged note" in (message.body or "")
            )
        )

    # the task pages give every attachment of the task a download link
    def test_member_visit_gives_restricted_task_attachment_no_link(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "budget.txt",
                "raw": b"Hourly rate agreed with the customer",
                "res_model": "project.task",
                "res_id": self.task_restricted.id,
            }
        )
        self.authenticate("member_test", "member_test")
        response = self.url_open("/my/task/%s" % self.task_restricted.id)
        self.assertIn("budget.txt", response.text)
        attachment.invalidate_cache(["access_token"])
        self.assertFalse(attachment.access_token)
        download = self.url_open(
            "/web/content/%s?download=true&access_token=" % attachment.id
        )
        self.assertEqual(download.content, b"Hourly rate agreed with the customer")

    def test_restricted_task_gets_no_token(self):
        self.assertIsNone(self.task_restricted._portal_ensure_token())
        self.assertFalse(self.task_restricted.access_token)

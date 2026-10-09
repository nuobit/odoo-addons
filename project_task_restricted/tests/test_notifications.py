# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import Form, users

from odoo.addons.mail.tests.common import MailCase

from .common import TestProjectTaskRestrictedCommon


class TestNotifications(TestProjectTaskRestrictedCommon, MailCase):
    @users("member_test")
    def test_typed_recipients_receive_message_and_are_not_subscribed(self):
        composer_form = Form(
            self.env["mail.compose.message"].with_context(
                default_model="project.task",
                default_res_id=self.task_restricted.id,
                mail_post_autofollow=True,
            )
        )
        composer_form.body = "Hourly rate agreed with the customer"
        composer_form.partner_ids.add(self.partner_2)
        composer_form.partner_ids.add(self.user_developer.partner_id)
        with self.mock_mail_gateway():
            composer_form.save().action_send_mail()
        self.assertEqual(
            sorted(mail["email_to"] for mail in self._mails),
            [
                ['"Developer" <d.d@example.com>'],
                ['"Valid Poilvache" <valid.other@gmail.com>'],
            ],
        )
        self.assertEqual(
            self.task_restricted.message_partner_ids, self.user_member.partner_id
        )

    @users("member_test")
    def test_message_nobody_addressed_reaches_only_members(self):
        with self.mock_mail_gateway():
            message = self.task_restricted.with_user(self.env.user).message_post(
                body="Hourly rate agreed with the customer",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=[
                    self.partner_2.id,
                    self.user_developer.partner_id.id,
                    self.user_project_sync.partner_id.id,
                ],
            )
        self.assertEqual(message.partner_ids, self.user_project_sync.partner_id)
        self.assertEqual(
            message.sudo().notification_ids.res_partner_id,
            self.user_project_sync.partner_id,
        )
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    @users("member_test")
    def test_program_message_logs_dropped_non_member_addressee(self):
        with self.assertLogs(
            "odoo.addons.project_task_restricted.models.project_task", logging.INFO
        ) as logs:
            message = self.task_restricted.message_post(
                body="Hourly rate agreed with the customer",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=self.user_developer.partner_id.ids,
            )
        self.assertEqual(
            logs.output,
            [
                "INFO:odoo.addons.project_task_restricted.models.project_task:"
                "Message %s is about a restricted task; addressees outside the "
                "Restricted tasks group removed: [%s]"
                % (message.id, self.user_developer.partner_id.id)
            ],
        )

    @users("member_test")
    def test_program_addresses_non_member_on_purpose(self):
        with self.mock_mail_gateway():
            message = self.task_restricted.with_context(
                restricted_typed_partner_ids=self.user_developer.partner_id.ids
            ).message_post(
                body="Hourly rate agreed with the customer",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=self.user_developer.partner_id.ids,
            )
        self.assertEqual(message.partner_ids, self.user_developer.partner_id)
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Developer" <d.d@example.com>']],
        )

    @users("member_test")
    def test_direct_notification_reaches_only_members(self):
        with self.mock_mail_gateway():
            message = self.task_restricted.with_user(self.env.user).message_notify(
                partner_ids=[
                    self.user_developer.partner_id.id,
                    self.user_project_sync.partner_id.id,
                ],
                body="Hourly rate agreed with the customer",
                subject="Pigs Budget",
            )
        self.assertEqual(
            message.sudo().notification_ids.res_partner_id,
            self.user_project_sync.partner_id,
        )
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    @users("member_test")
    def test_message_notifies_only_member_followers(self):
        # a follower added through no subscription method at all
        self.env["mail.followers"].sudo()._insert_followers(
            "project.task",
            self.task_restricted.ids,
            [self.user_developer.partner_id.id, self.user_project_sync.partner_id.id],
        )
        with self.mock_mail_gateway():
            message = self.task_restricted.with_user(self.env.user).message_post(
                body="Hourly rate agreed with the customer",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
        self.assertEqual(
            message.sudo().notification_ids.res_partner_id,
            self.user_project_sync.partner_id,
        )
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    @users("developer_test")
    def test_marking_revokes_non_member_notifications(self):
        self.user_developer.notification_type = "inbox"
        self.task_quote.with_user(self.env.user).message_subscribe(
            partner_ids=self.env.user.partner_id.ids
        )
        message = self.task_quote.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.task_quote.with_user(self.user_member).write({"restricted": True})
        self.assertFalse(self.env["mail.message"].search([("needaction", "=", True)]))
        with self.assertRaises(AccessError):
            message.with_user(self.env.user).read(["body"])

    @users("member_test")
    def test_marking_keeps_notifications_of_members_and_partners_without_user(self):
        self.task_quote.message_subscribe(
            partner_ids=[
                self.partner_2.id,
                self.user_developer.partner_id.id,
                self.user_project_sync.partner_id.id,
            ]
        )
        message = self.task_quote.message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.task_quote.write({"restricted": True})
        self.assertEqual(
            set(message.sudo().notification_ids.res_partner_id.ids),
            {self.partner_2.id, self.user_project_sync.partner_id.id},
        )

    @users("member_test")
    def test_marking_stops_queued_email_to_non_member(self):
        self.task_quote.message_subscribe(
            partner_ids=[
                self.user_developer.partner_id.id,
                self.user_project_sync.partner_id.id,
            ]
        )
        self.task_quote.with_context(mail_notify_force_send=False).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.task_quote.write({"restricted": True})
        with self.mock_mail_gateway():
            self.env["mail.mail"].sudo().process_email_queue()
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    @users("member_test")
    def test_marking_stops_failed_email_to_non_member(self):
        self.task_quote.message_subscribe(
            partner_ids=[
                self.user_developer.partner_id.id,
                self.user_project_sync.partner_id.id,
            ]
        )
        message = self.task_quote.with_context(
            mail_notify_force_send=False
        ).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        mails = (
            self.env["mail.mail"].sudo().search([("mail_message_id", "=", message.id)])
        )
        mails.write({"state": "exception"})
        self.task_quote.write({"restricted": True})
        mails.mark_outgoing()
        with self.mock_mail_gateway():
            self.env["mail.mail"].sudo().process_email_queue()
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    # the portal formatter gives every attachment of a message a download link
    @users("developer_test")
    def test_recipient_formatting_message_after_marking_gets_no_attachment_link(self):
        message = self.task_quote.with_user(self.user_member).message_post(
            body="The budget",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.env.user.partner_id.ids,
            attachments=[("budget.txt", b"Hourly rate agreed with the customer")],
        )
        self.task_quote.with_user(self.user_member).write({"restricted": True})
        formatted = message.portal_message_format()
        self.assertFalse(formatted[0]["attachment_ids"][0]["access_token"])
        self.assertFalse(message.sudo().attachment_ids.access_token)

    @users("member_test")
    def test_marking_clears_attachment_links(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "budget.txt",
                "raw": b"Hourly rate agreed with the customer",
                "res_model": "project.task",
                "res_id": self.task_quote.id,
                "public": True,
            }
        )
        attachment.generate_access_token()
        self.task_quote.write({"restricted": True})
        self.assertFalse(attachment.access_token)
        self.assertFalse(attachment.public)

    @users("developer_test")
    def test_recipient_keeps_reading_after_marking(self):
        message = self.task_quote.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.env.user.partner_id.ids,
        )
        self.task_quote.with_user(self.user_member).write({"restricted": True})
        messages = self.env["mail.message"].search(
            [("model", "=", "project.task"), ("res_id", "=", self.task_quote.id)]
        )
        self.assertEqual(messages, message)

    @users("member_test")
    def test_stage_template_reaches_no_customer_of_restricted_task(self):
        stage = (
            self.env["project.task.type"]
            .sudo()
            .create(
                {
                    "name": "Done",
                    "project_ids": [Command.link(self.project_pigs.id)],
                    "mail_template_id": self.env.ref(
                        "project.mail_template_data_project_task"
                    ).id,
                }
            )
        )
        # Odoo tracks a record only once the transaction that created it ends
        self.flush_tracking()
        with self.mock_mail_gateway():
            self.task_quote.with_user(self.env.user).write({"stage_id": stage.id})
            self.task_restricted.with_user(self.env.user).write({"stage_id": stage.id})
            self.flush_tracking()
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Valid Lelitre" <valid.lelitre@agrolait.com>']],
        )

    @users("member_test")
    def test_rating_request_reaches_no_customer_of_restricted_task(self):
        self.project_pigs.sudo().rating_active = True
        stage = (
            self.env["project.task.type"]
            .sudo()
            .create(
                {
                    "name": "Done",
                    "project_ids": [Command.link(self.project_pigs.id)],
                    "rating_template_id": self.env.ref(
                        "project.rating_project_request_email_template"
                    ).id,
                }
            )
        )
        with self.mock_mail_gateway():
            self.task_quote.with_user(self.env.user).write({"stage_id": stage.id})
            self.task_restricted.with_user(self.env.user).write({"stage_id": stage.id})
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Valid Lelitre" <valid.lelitre@agrolait.com>']],
        )

    def test_template_email_reaches_only_members(self):
        template = self.env["mail.template"].create(
            {
                "name": "Budget figures",
                "model_id": self.env["ir.model"]._get_id("project.task"),
                "subject": "Budget figures",
                "body_html": "<p>Hourly rate agreed with the customer</p>",
                "email_from": self.user_member.email_formatted,
                "email_to": "d.d@example.com, p.p@example.com",
                "partner_to": "%s,%s"
                % (self.user_developer.partner_id.id, self.partner_2.id),
            }
        )
        with self.mock_mail_gateway():
            template.send_mail(self.task_restricted.id, force_send=True)
        self.assertEqual(
            [mail["email_to"] for mail in self._mails], [["p.p@example.com"]]
        )

    def test_template_email_only_to_non_members_is_cancelled(self):
        template = self.env["mail.template"].create(
            {
                "name": "Budget figures",
                "model_id": self.env["ir.model"]._get_id("project.task"),
                "subject": "Budget figures",
                "body_html": "<p>Hourly rate agreed with the customer</p>",
                "email_from": self.user_member.email_formatted,
                "partner_to": "%s" % self.user_developer.partner_id.id,
            }
        )
        with self.mock_mail_gateway():
            template.send_mail(self.task_restricted.id)
        self.assertEqual(self._new_mails.state, "cancel")
        self.assertEqual(
            self._new_mails.failure_reason,
            "Not sent: it is about a restricted task, and none of its recipients "
            "is a member of the Restricted tasks group or was addressed on "
            "purpose.",
        )

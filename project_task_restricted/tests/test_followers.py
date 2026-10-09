# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import Form, users

from odoo.addons.mail.tests.common import MailCase

from .common import TestProjectTaskRestrictedCommon

REPLY_TPL = """From: {email_from}
To: {to}
Cc: {cc}
Subject: Re: Pigs Budget
Message-ID: <reply.pigs.budget@example.com>
In-Reply-To: {in_reply_to}
References: {in_reply_to}
Content-Type: text/plain; charset=utf-8

The new figures are in the attached sheet.
"""


class TestFollowers(TestProjectTaskRestrictedCommon, MailCase):
    @users("member_test")
    def test_marking_unsubscribes_non_members(self):
        self.task_quote.with_user(self.user_developer).message_subscribe(
            partner_ids=self.user_developer.partner_id.ids
        )
        with Form(self.task_quote.with_user(self.env.user)) as task_form:
            task_form.restricted = True
        self.assertEqual(
            self.task_quote.message_partner_ids, self.user_member.partner_id
        )

    @users("member_test")
    def test_member_invites_member_to_restricted_task(self):
        invite_form = Form(
            self.env["mail.wizard.invite"].with_context(
                default_res_model="project.task",
                default_res_id=self.task_restricted.id,
            )
        )
        invite_form.partner_ids.add(self.user_project_sync.partner_id)
        with self.mock_mail_gateway():
            invite_form.save().add_followers()
        self.assertEqual(
            set(self.task_restricted.message_partner_ids.ids),
            {self.user_member.partner_id.id, self.user_project_sync.partner_id.id},
        )

    @users("member_test")
    def test_member_cannot_invite_non_member_to_restricted_task(self):
        invite_form = Form(
            self.env["mail.wizard.invite"].with_context(
                default_res_model="project.task",
                default_res_id=self.task_restricted.id,
            )
        )
        invite_form.partner_ids.add(self.user_developer.partner_id)
        invite_form.partner_ids.add(self.partner_2)
        with self.assertRaises(UserError) as error:
            invite_form.save().add_followers()
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can follow the "
            'restricted task "Pigs Budget". Not in the group: Developer, Valid '
            "Poilvache. Remove them from the recipients.",
        )

    @users("member_test")
    def test_member_invites_non_member_to_normal_task(self):
        invite_form = Form(
            self.env["mail.wizard.invite"].with_context(
                default_res_model="project.task",
                default_res_id=self.task_quote.id,
            )
        )
        invite_form.partner_ids.add(self.user_developer.partner_id)
        with self.mock_mail_gateway():
            invite_form.save().add_followers()
        self.assertIn(
            self.user_developer.partner_id, self.task_quote.message_partner_ids
        )

    @users("member_test")
    def test_member_shares_normal_task_with_non_member(self):
        # only a contact manager may share a document
        self.user_member.groups_id += self.env.ref("base.group_partner_manager")
        share_form = Form(
            self.env["portal.share"].with_context(
                active_model="project.task", active_id=self.task_quote.id
            )
        )
        share_form.partner_ids.add(self.partner_2)
        with self.mock_mail_gateway():
            share_form.save().action_send_mail()
        # sharing subscribes the recipients
        self.assertIn(self.partner_2, self.task_quote.message_partner_ids)

    @users("member_test")
    def test_member_cannot_share_restricted_task_with_non_member(self):
        # only a contact manager may share a document
        self.user_member.groups_id += self.env.ref("base.group_partner_manager")
        share_form = Form(
            self.env["portal.share"].with_context(
                active_model="project.task", active_id=self.task_restricted.id
            )
        )
        share_form.partner_ids.add(self.partner_2)
        with self.assertRaises(UserError) as error:
            share_form.save().action_send_mail()
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can be sent the "
            'restricted task "Pigs Budget". Not in the group: Valid Poilvache. '
            "Remove them from the recipients.",
        )

    @users("member_test")
    def test_moving_restricted_task_skips_project_followers(self):
        self.project_goats.sudo().message_subscribe(
            partner_ids=self.user_developer.partner_id.ids
        )
        self.task_restricted.write({"project_id": self.project_goats.id})
        self.assertEqual(
            self.task_restricted.message_partner_ids, self.user_member.partner_id
        )

    @users("member_test")
    def test_project_follower_not_subscribed_to_new_restricted_task(self):
        self.project_pigs.with_user(self.user_developer).message_subscribe(
            partner_ids=self.user_developer.partner_id.ids
        )
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id
            )
        )
        task_form.name = "Pigs Offer"
        task_form.restricted = True
        task = task_form.save()
        self.assertEqual(task.message_partner_ids, self.user_member.partner_id)

    @users("project_sync_test")
    def test_project_follower_added_by_member_skips_restricted_task(self):
        self.project_pigs.with_user(self.env.user).message_subscribe(
            partner_ids=self.user_developer.partner_id.ids
        )
        self.assertIn(
            self.user_developer.partner_id, self.task_quote.message_partner_ids
        )
        self.assertNotIn(
            self.user_developer.partner_id, self.task_restricted.message_partner_ids
        )

    def test_email_reply_does_not_subscribe_non_member_in_cc(self):
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.env["mail.thread"].message_process(
            None,
            REPLY_TPL.format(
                email_from=self.user_member.email,
                to="pigs@example.com",
                cc=self.partner_2.email,
                in_reply_to=message.message_id,
            ),
        )
        self.assertNotIn(self.partner_2, self.task_restricted.message_partner_ids)

    def test_email_reply_notifies_only_members(self):
        self.task_restricted.message_subscribe(
            partner_ids=self.user_project_sync.partner_id.ids
        )
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        with self.mock_mail_gateway():
            self.env["mail.thread"].message_process(
                None,
                REPLY_TPL.format(
                    email_from=self.user_member.email,
                    to="pigs@example.com",
                    cc=self.partner_2.email,
                    in_reply_to=message.message_id,
                ),
            )
        self.assertEqual(
            [mail["email_to"] for mail in self._mails],
            [['"Project Sync" <p.p@example.com>']],
        )

    # the gateway writes the e-mail's To and Cc back after posting: they keep
    # reading the e-mail they received
    def test_email_reply_keeps_its_cc_as_addressee(self):
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.env["mail.thread"].message_process(
            None,
            REPLY_TPL.format(
                email_from=self.user_member.email,
                to="pigs@example.com",
                cc=self.partner_2.email,
                in_reply_to=message.message_id,
            ),
        )
        reply = self.env["mail.message"].search(
            [("message_id", "=", "<reply.pigs.budget@example.com>")]
        )
        self.assertEqual(reply.partner_ids, self.partner_2)

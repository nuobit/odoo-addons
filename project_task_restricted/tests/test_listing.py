# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import users

from .common import TestProjectTaskRestrictedCommon


# Every internal user can list Odoo's notifications, which show the subject of
# a stored e-mail, and its customer ratings, with their feedback
class TestListing(TestProjectTaskRestrictedCommon):
    @users("developer_test")
    def test_non_member_lists_no_notification_of_restricted_task(self):
        restricted = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.user_project_sync.partner_id.ids,
        )
        quote = self.task_quote.with_user(self.user_member).message_post(
            body="Estimate of the remaining hours",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.user_project_sync.partner_id.ids,
        )
        notifications = self.env["mail.notification"].search(
            [("mail_message_id", "in", (restricted | quote).ids)]
        )
        self.assertEqual(notifications.mail_message_id, quote)

    @users("developer_test")
    def test_typed_recipient_lists_own_notification_of_restricted_task(self):
        message = (
            self.task_restricted.with_user(self.user_member)
            .with_context(restricted_typed_partner_ids=self.env.user.partner_id.ids)
            .message_post(
                body="Hourly rate agreed with the customer",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=self.env.user.partner_id.ids,
            )
        )
        notifications = self.env["mail.notification"].search(
            [("mail_message_id", "=", message.id)]
        )
        self.assertEqual(notifications.res_partner_id, self.env.user.partner_id)

    @users("member_test")
    def test_member_lists_notifications_of_restricted_task(self):
        message = self.task_restricted.with_user(self.env.user).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.user_project_sync.partner_id.ids,
        )
        notifications = self.env["mail.notification"].search(
            [("mail_message_id", "=", message.id)]
        )
        self.assertEqual(
            notifications.res_partner_id, self.user_project_sync.partner_id
        )

    @users("developer_test")
    def test_non_member_lists_no_rating_of_restricted_task(self):
        task_model_id = self.env["ir.model"]._get_id("project.task")
        ratings = (
            self.env["rating.rating"]
            .sudo()
            .create(
                [
                    {
                        "res_model_id": task_model_id,
                        "res_id": self.task_restricted.id,
                        "rating": 1,
                        "feedback": "Too expensive",
                        "consumed": True,
                    },
                    {
                        "res_model_id": task_model_id,
                        "res_id": self.task_quote.id,
                        "rating": 5,
                        "feedback": "Clear estimate",
                        "consumed": True,
                    },
                ]
            )
        )
        found = self.env["rating.rating"].search([("id", "in", ratings.ids)])
        self.assertEqual(found.mapped("feedback"), ["Clear estimate"])

    @users("member_test")
    def test_member_lists_rating_of_restricted_task(self):
        rating = (
            self.env["rating.rating"]
            .sudo()
            .create(
                {
                    "res_model_id": self.env["ir.model"]._get_id("project.task"),
                    "res_id": self.task_restricted.id,
                    "rating": 1,
                    "feedback": "Too expensive",
                    "consumed": True,
                }
            )
        )
        found = self.env["rating.rating"].search([("id", "=", rating.id)])
        self.assertEqual(found.mapped("feedback"), ["Too expensive"])

    @users("member_test")
    def test_member_reads_which_messages_are_restricted(self):
        restricted = self.task_restricted.with_user(self.env.user).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        quote = self.task_quote.with_user(self.env.user).message_post(
            body="Estimate of the remaining hours",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.assertEqual((restricted | quote).mapped("restricted"), [True, False])

    @users("member_test")
    def test_member_searches_messages_not_restricted(self):
        restricted = self.task_restricted.with_user(self.env.user).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        quote = self.task_quote.with_user(self.env.user).message_post(
            body="Estimate of the remaining hours",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        found = self.env["mail.message"].search(
            [("id", "in", (restricted | quote).ids), ("restricted", "!=", True)]
        )
        self.assertEqual(found, quote)

    @users("member_test")
    def test_restricted_is_searched_only_with_equality(self):
        with self.assertRaises(ValueError) as error:
            self.env["mail.message"].search([("restricted", "in", [True])])
        self.assertEqual(
            str(error.exception), "Restricted is searched with = or !=, not with in"
        )

    @users("member_test")
    def test_member_reads_which_ratings_are_restricted(self):
        task_model_id = self.env["ir.model"]._get_id("project.task")
        ratings = (
            self.env["rating.rating"]
            .sudo()
            .create(
                [
                    {
                        "res_model_id": task_model_id,
                        "res_id": self.task_restricted.id,
                        "rating": 1,
                        "consumed": True,
                    },
                    {
                        "res_model_id": task_model_id,
                        "res_id": self.task_quote.id,
                        "rating": 5,
                        "consumed": True,
                    },
                ]
            )
        )
        self.assertEqual(
            ratings.with_user(self.env.user).mapped("restricted"), [True, False]
        )

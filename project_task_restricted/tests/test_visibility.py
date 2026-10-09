# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import Form, users
from odoo.tools import convert_file, mute_logger

from odoo.addons.mail.tests.common import mail_new_test_user

from .common import TestProjectTaskRestrictedCommon


class TestVisibility(TestProjectTaskRestrictedCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_restricted_goats = (
            cls.env["project.task"]
            .with_user(cls.user_project_sync)
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Goats Budget",
                    "project_id": cls.project_goats.id,
                    "restricted": True,
                }
            )
        )

    def test_administrator_user_is_member(self):
        self.assertIn(
            self.env.ref("base.user_admin"),
            self.env.ref("project_task_restricted.group_restricted_task").users,
        )

    def test_update_puts_administrator_user_back(self):
        group = self.env.ref("project_task_restricted.group_restricted_task")
        group.users -= self.env.ref("base.user_admin")
        convert_file(
            self.cr,
            "project_task_restricted",
            "security/project_task_restricted_security.xml",
            {},
            mode="update",
            kind="data",
        )
        group.invalidate_cache(["users"])
        self.assertIn(self.env.ref("base.user_admin"), group.users)

    def test_first_install_creates_group_with_administrator_user(self):
        """On a first install the group does not exist yet: Odoo creates it
        and then writes its members, before its external id exists."""
        self.addCleanup(self.registry.clear_caches)
        self.env["ir.model.data"].search(
            [
                ("module", "=", "project_task_restricted"),
                ("name", "=", "group_restricted_task"),
            ]
        ).unlink()
        self.registry.clear_caches()
        convert_file(
            self.cr,
            "project_task_restricted",
            "security/project_task_restricted_security.xml",
            {},
            mode="init",
            kind="data",
        )
        self.assertIn(
            self.env.ref("base.user_admin"),
            self.env.ref("project_task_restricted.group_restricted_task").users,
        )

    @users("developer_test")
    def test_non_member_cannot_find_restricted_task(self):
        tasks = self.env["project.task"].search(
            [("project_id", "=", self.project_pigs.id)]
        )
        self.assertEqual(
            set(tasks.ids), {self.task_1.id, self.task_2.id, self.task_quote.id}
        )

    @users("developer_test")
    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_non_member_cannot_read_restricted_task(self):
        with self.assertRaises(AccessError):
            self.task_restricted.with_user(self.env.user).read(["name"])

    @users("developer_test")
    def test_non_member_cannot_find_restricted_task_message(self):
        self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        messages = self.env["mail.message"].search(
            [("model", "=", "project.task"), ("res_id", "=", self.task_restricted.id)]
        )
        self.assertFalse(messages)

    @users("developer_test")
    def test_non_member_cannot_read_restricted_task_message(self):
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        with self.assertRaises(AccessError):
            message.with_user(self.env.user).read(["body"])

    # Discuss formats a reply's parent as superuser
    @users("developer_test")
    def test_non_member_cannot_reply_elsewhere_to_restricted_task_message(self):
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        channel = self.env["mail.channel"].browse(
            self.env["mail.channel"].channel_create(name="Developers")["id"]
        )
        with self.assertRaises(ValidationError):
            self.env["mail.message"].create(
                {
                    "model": "mail.channel",
                    "res_id": channel.id,
                    "parent_id": message.id,
                    "body": "Quoting it",
                    "message_type": "comment",
                    "author_id": self.env.user.partner_id.id,
                }
            )

    @users("developer_test")
    def test_non_member_cannot_repoint_message_to_restricted_task_message(self):
        message = self.task_restricted.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        channel = self.env["mail.channel"].browse(
            self.env["mail.channel"].channel_create(name="Developers")["id"]
        )
        reply = self.env["mail.message"].create(
            {
                "model": "mail.channel",
                "res_id": channel.id,
                "body": "Quoting it",
                "message_type": "comment",
                "author_id": self.env.user.partner_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            reply.write({"parent_id": message.id})

    # a reply made while the task was visible keeps its parent unless the
    # marking takes it away
    @users("developer_test")
    def test_marking_detaches_replies_elsewhere(self):
        message = self.task_quote.with_user(self.user_member).message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        channel = self.env["mail.channel"].browse(
            self.env["mail.channel"].channel_create(name="Developers")["id"]
        )
        reply = self.env["mail.message"].create(
            {
                "model": "mail.channel",
                "res_id": channel.id,
                "parent_id": message.id,
                "body": "Quoting it",
                "message_type": "comment",
                "author_id": self.env.user.partner_id.id,
            }
        )
        self.task_quote.with_user(self.user_member).restricted = True
        self.assertNotIn("Hourly rate", str(reply.message_format()))

    # Odoo posts a blocking task's changes on the tasks it blocks
    @users("member_test")
    def test_restricted_task_reports_no_change_to_task_it_blocks(self):
        self.env["res.config.settings"].sudo().create(
            {"group_project_task_dependencies": True}
        ).execute()
        self.project_pigs.sudo().allow_task_dependencies = True
        # as in Odoo's own test, the dependency itself is not tracked
        self.task_1.sudo().with_context(mail_notrack=True).depend_on_ids = (
            self.task_restricted | self.task_quote
        )
        self.cr.precommit.clear()
        (self.task_restricted | self.task_quote).date_deadline = "2026-12-31"
        self.env["base"].flush()
        self.cr.precommit.run()
        self.task_1.invalidate_cache(["message_ids"])
        bodies = self.task_1.sudo().message_ids.mapped("body")
        self.assertTrue([body for body in bodies if "Pigs Quote" in body])
        self.assertFalse([body for body in bodies if "Pigs Budget" in body])

    def test_portal_user_cannot_join_group(self):
        user_portal = mail_new_test_user(
            self.env, login="portal_test", name="Customer", groups="base.group_portal"
        )
        with self.assertRaises(ValidationError):
            self.env.ref(
                "project_task_restricted.group_restricted_task"
            ).users += user_portal

    @users("member_test")
    def test_member_replies_on_restricted_task(self):
        message = self.task_restricted.message_post(
            body="Hourly rate agreed with the customer",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        reply = self.task_restricted.message_post(
            body="Confirmed",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            parent_id=message.id,
        )
        self.assertEqual(reply.parent_id, message)

    @users("developer_test")
    def test_author_finds_own_message_after_marking(self):
        message = self.task_quote.with_user(self.env.user).message_post(
            body="Estimate of the remaining hours",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.task_quote.with_user(self.user_member).write({"restricted": True})
        messages = self.env["mail.message"].search(
            [("model", "=", "project.task"), ("res_id", "=", self.task_quote.id)]
        )
        self.assertEqual(messages, message)

    @users("developer_test")
    def test_typed_recipient_finds_message_on_restricted_task(self):
        composer_form = Form(
            self.env["mail.compose.message"]
            .with_user(self.user_member)
            .with_context(
                default_model="project.task", default_res_id=self.task_restricted.id
            )
        )
        composer_form.body = "Hourly rate agreed with the customer"
        composer_form.partner_ids.add(self.env.user.partner_id)
        composer_form.save().action_send_mail()
        messages = self.env["mail.message"].search(
            [("model", "=", "project.task"), ("res_id", "=", self.task_restricted.id)]
        )
        self.assertEqual(
            messages.mapped("body"), ["<p>Hourly rate agreed with the customer</p>"]
        )

    @users("developer_test")
    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_non_member_cannot_read_restricted_task_attachment(self):
        attachment = (
            self.env["ir.attachment"]
            .with_user(self.user_member)
            .create(
                {
                    "name": "budget.txt",
                    "raw": b"Hourly rate agreed with the customer",
                    "res_model": "project.task",
                    "res_id": self.task_restricted.id,
                }
            )
        )
        with self.assertRaises(AccessError):
            attachment.with_user(self.env.user).read(["name"])

    @users("member_test")
    def test_member_finds_restricted_task(self):
        tasks = self.env["project.task"].search(
            [("project_id", "=", self.project_pigs.id)]
        )
        self.assertEqual(
            set(tasks.ids),
            {
                self.task_1.id,
                self.task_2.id,
                self.task_restricted.id,
                self.task_quote.id,
            },
        )

    @users("member_test")
    def test_member_edits_restricted_task(self):
        with Form(self.task_restricted.with_user(self.env.user)) as task_form:
            task_form.name = "Pigs Budget v2"
        self.assertEqual(self.task_restricted.name, "Pigs Budget v2")

    @users("administrator_test")
    def test_project_administrator_cannot_find_restricted_task(self):
        tasks = self.env["project.task"].search(
            [("project_id", "=", self.project_pigs.id)]
        )
        self.assertEqual(
            set(tasks.ids), {self.task_1.id, self.task_2.id, self.task_quote.id}
        )

    @users("administrator_test")
    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_project_administrator_cannot_read_restricted_task(self):
        with self.assertRaises(AccessError):
            self.task_restricted.with_user(self.env.user).read(["name"])

    @users("member_test")
    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_member_cannot_read_restricted_task_of_unfollowed_project(self):
        with self.assertRaises(AccessError):
            self.task_restricted_goats.with_user(self.env.user).read(["name"])

    @users("member_test")
    def test_member_assigned_finds_restricted_task_of_unfollowed_project(self):
        self.task_restricted_goats.write({"user_ids": [Command.link(self.env.user.id)]})
        tasks = self.env["project.task"].search(
            [("project_id", "=", self.project_goats.id)]
        )
        self.assertEqual(tasks, self.task_restricted_goats)

    @users("developer_test")
    @mute_logger("odoo.models")
    def test_non_member_cannot_mark_task(self):
        with self.assertRaises(AccessError):
            self.task_quote.with_user(self.env.user).write({"restricted": True})

    @users("developer_test")
    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_non_member_cannot_create_restricted_task(self):
        with self.assertRaises(AccessError):
            # no assignee: the default one, the creator, would be refused first
            self.env["project.task"].create(
                {
                    "name": "Pigs Offer",
                    "project_id": self.project_pigs.id,
                    "restricted": True,
                    "user_ids": [],
                }
            )

    @users("developer_test")
    def test_non_member_task_form_has_no_restricted_field(self):
        arch = self.env["project.task"].fields_view_get(
            view_id=self.env.ref("project.view_task_form2").id, view_type="form"
        )["arch"]
        self.assertFalse(etree.fromstring(arch).xpath("//field[@name='restricted']"))

    @users("member_test")
    def test_member_marks_task(self):
        with Form(self.task_quote.with_user(self.env.user)) as task_form:
            task_form.restricted = True
        self.assertTrue(self.task_quote.restricted)

    @users("member_test")
    def test_member_creates_restricted_task(self):
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id
            )
        )
        task_form.name = "Pigs Offer"
        task_form.restricted = True
        task = task_form.save()
        self.assertTrue(task.restricted)

    @users("project_sync_test")
    def test_project_sync_reads_restricted_task(self):
        records = self.env["project.task"].search_read(
            [("project_id", "=", self.project_pigs.id)], ["name"], order="id"
        )
        self.assertEqual(
            records,
            [
                {"id": self.task_1.id, "name": "Pigs UserTask"},
                {"id": self.task_2.id, "name": "Pigs ManagerTask"},
                {"id": self.task_restricted.id, "name": "Pigs Budget"},
                {"id": self.task_quote.id, "name": "Pigs Quote"},
            ],
        )

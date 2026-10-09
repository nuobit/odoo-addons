# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from markupsafe import Markup

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import Form, users
from odoo.tools import mute_logger

from odoo.addons.base.models.res_users import name_selection_groups
from odoo.addons.mail.tests.common import mail_new_test_user

from .common import TestProjectTaskRestrictedCommon


# while modules load, Odoo leaves the user form without its group fields, and
# builds them once every module is loaded
@tagged("post_install", "-at_install")
class TestLeavingGroup(TestProjectTaskRestrictedCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # an administrator: the user form shows a portal user only to those
        # who may write contacts
        cls.user_settings = mail_new_test_user(
            cls.env,
            login="settings_test",
            name="Settings",
            groups="base.group_user,base.group_system,base.group_partner_manager",
        )
        cls.group = cls.env.ref("project_task_restricted.group_restricted_task")
        cls.task_followed = (
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
        cls.task_followed.message_subscribe(partner_ids=cls.user_member.partner_id.ids)
        cls.task_archived = (
            cls.env["project.task"]
            .with_user(cls.user_member)
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Pigs Old Budget",
                    "project_id": cls.project_pigs.id,
                    "restricted": True,
                    "active": False,
                }
            )
        )

    def _remove_from_group_form(self, user):
        # the form's warning is tested on its own
        with mute_logger("odoo.tests.common.onchange"):
            with Form(self.group.with_user(self.env.user)) as group_form:
                group_form.users.remove(id=user.id)

    @users("settings_test")
    def test_group_form_takes_leaver_off_restricted_tasks(self):
        self._remove_from_group_form(self.user_member)
        task = self.task_restricted.sudo()
        self.assertFalse(task.user_ids)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_user_form_takes_leaver_off_restricted_tasks(self):
        # the form's warning is tested on its own; the default user form is the
        # simplified one, without groups
        with mute_logger("odoo.tests.common.onchange"):
            with Form(
                self.user_member.with_user(self.env.user), view="base.view_users_form"
            ) as user_form:
                setattr(
                    user_form, self.env["res.users"]._restricted_group_field(), False
                )
        task = self.task_restricted.sudo()
        self.assertFalse(task.user_ids)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_groups_write_takes_leaver_off_restricted_tasks(self):
        self.user_member.with_user(self.env.user).write(
            {"groups_id": [Command.unlink(self.group.id)]}
        )
        task = self.task_restricted.sudo()
        self.assertFalse(task.user_ids)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_change_to_portal_takes_leaver_off_restricted_tasks(self):
        # the User Type of the user form, shown in debug mode: a user who stops
        # being internal leaves every other group, without unticking ours. The
        # form's warning is tested on its own
        user_types = self.env["res.groups"].search(
            [("category_id", "=", self.env.ref("base.module_category_user_type").id)]
        )
        with mute_logger("odoo.tests.common.onchange"):
            with Form(
                self.user_member.with_user(self.env.user), view="base.view_users_form"
            ) as user_form:
                setattr(
                    user_form,
                    name_selection_groups(user_types.ids),
                    self.env.ref("base.group_portal").id,
                )
        task = self.task_restricted.sudo()
        self.assertFalse(task.user_ids)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_leaver_keeps_normal_tasks(self):
        self._remove_from_group_form(self.user_member)
        task = self.task_quote.sudo()
        self.assertEqual(task.user_ids, self.user_member)
        self.assertIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_leaver_is_taken_off_followed_task(self):
        self._remove_from_group_form(self.user_member)
        task = self.task_followed.sudo()
        self.assertEqual(task.user_ids, self.user_project_sync)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_leaver_is_taken_off_archived_task(self):
        self._remove_from_group_form(self.user_member)
        task = self.task_archived.sudo()
        self.assertFalse(task.user_ids)
        self.assertNotIn(self.user_member.partner_id, task.message_partner_ids)

    @users("settings_test")
    def test_leaving_posts_note_on_each_restricted_task(self):
        self._remove_from_group_form(self.user_member)
        note = self.env.ref("mail.mt_note")
        self.assertEqual(
            [
                (message.body, message.author_id)
                for message in (
                    self.task_restricted + self.task_followed + self.task_archived
                )
                .sudo()
                .message_ids.filtered(lambda message: message.subtype_id == note)
            ],
            [
                (
                    Markup(
                        "<p>Taken off this restricted task after leaving the "
                        "Restricted tasks group: Member.</p>"
                    ),
                    self.user_settings.partner_id,
                ),
                (
                    Markup(
                        "<p>Taken off this restricted task after leaving the "
                        "Restricted tasks group: Member.</p>"
                    ),
                    self.user_settings.partner_id,
                ),
                (
                    Markup(
                        "<p>Taken off this restricted task after leaving the "
                        "Restricted tasks group: Member.</p>"
                    ),
                    self.user_settings.partner_id,
                ),
            ],
        )

    @users("settings_test")
    def test_leaving_posts_no_note_on_normal_task(self):
        self._remove_from_group_form(self.user_member)
        self.assertFalse(self.task_quote.sudo().message_ids)

    @users("settings_test")
    def test_leaver_keeps_notifications(self):
        message = self.task_restricted.with_user(self.user_project_sync).message_post(
            body="Pigs price", message_type="comment", subtype_xmlid="mail.mt_comment"
        )
        notification = message.sudo().notification_ids.filtered(
            lambda notification: notification.res_partner_id
            == self.user_member.partner_id
        )
        self._remove_from_group_form(self.user_member)
        self.assertTrue(notification.exists())

    @users("settings_test")
    def test_groups_write_refused_with_activity_on_restricted_task(self):
        self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        # a member who stays in the group keeps their activity
        self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_project_sync.id
        )
        with self.assertRaises(ValidationError) as error:
            self.user_member.with_user(self.env.user).write(
                {"groups_id": [Command.unlink(self.group.id)]}
            )
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            "restricted tasks. Leaving the group: Member, with activities on "
            '"Pigs Budget". Assign those activities to a member or mark them as '
            "done first.",
        )

    @users("settings_test")
    def test_group_form_refused_with_activity_on_restricted_task(self):
        self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        with self.assertRaises(ValidationError) as error:
            self._remove_from_group_form(self.user_member)
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            "restricted tasks. Leaving the group: Member, with activities on "
            '"Pigs Budget". Assign those activities to a member or mark them as '
            "done first.",
        )

    @users("settings_test")
    def test_activity_on_archived_restricted_task_refuses_leaving(self):
        # archiving a task removes its activities; one can still be scheduled
        # on it afterwards
        self.task_archived.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        with self.assertRaises(ValidationError) as error:
            self._remove_from_group_form(self.user_member)
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            "restricted tasks. Leaving the group: Member, with activities on "
            '"Pigs Old Budget". Assign those activities to a member or mark them '
            "as done first.",
        )

    @users("settings_test")
    def test_leaving_allowed_once_activity_reassigned(self):
        activity = self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        activity.write({"user_id": self.user_project_sync.id})
        self._remove_from_group_form(self.user_member)
        self.assertNotIn(self.user_member, self.group.users)

    @users("settings_test")
    def test_leaving_allowed_once_activity_done(self):
        activity = self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        activity.action_done()
        self._remove_from_group_form(self.user_member)
        self.assertNotIn(self.user_member, self.group.users)

    @users("settings_test")
    def test_activity_on_normal_task_allows_leaving(self):
        self.task_quote.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        self._remove_from_group_form(self.user_member)
        self.assertNotIn(self.user_member, self.group.users)

    @users("settings_test")
    def test_group_form_warns_before_removal(self):
        with Form(self.group.with_user(self.env.user)) as group_form:
            with self.assertLogs("odoo.tests.common.onchange", logging.WARNING) as logs:
                group_form.users.remove(id=self.user_member.id)
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.tests.common.onchange:Restricted tasks Leaving the "
                "group: Member. When you save, they will be taken off the "
                "restricted tasks they are assigned to or follow, with an "
                "internal note on each. Tasks affected: 3."
            ],
        )

    @users("settings_test")
    def test_user_form_warns_before_untick(self):
        with Form(
            self.user_member.with_user(self.env.user), view="base.view_users_form"
        ) as user_form:
            with self.assertLogs("odoo.tests.common.onchange", logging.WARNING) as logs:
                setattr(
                    user_form, self.env["res.users"]._restricted_group_field(), False
                )
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.tests.common.onchange:Restricted tasks Leaving the "
                "group: Member. When you save, they will be taken off the "
                "restricted tasks they are assigned to or follow, with an "
                "internal note on each. Tasks affected: 3."
            ],
        )

    @users("settings_test")
    def test_user_form_warns_before_change_to_portal(self):
        user_types = self.env["res.groups"].search(
            [("category_id", "=", self.env.ref("base.module_category_user_type").id)]
        )
        with Form(
            self.user_member.with_user(self.env.user), view="base.view_users_form"
        ) as user_form:
            with self.assertLogs("odoo.tests.common.onchange", logging.WARNING) as logs:
                setattr(
                    user_form,
                    name_selection_groups(user_types.ids),
                    self.env.ref("base.group_portal").id,
                )
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.tests.common.onchange:Restricted tasks Leaving the "
                "group: Member. When you save, they will be taken off the "
                "restricted tasks they are assigned to or follow, with an "
                "internal note on each. Tasks affected: 3."
            ],
        )

    @users("settings_test")
    def test_group_form_warns_of_activities_before_removal(self):
        self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_member.id
        )
        # not saved: saving is refused
        group_form = Form(self.group.with_user(self.env.user))
        with self.assertLogs("odoo.tests.common.onchange", logging.WARNING) as logs:
            group_form.users.remove(id=self.user_member.id)
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.tests.common.onchange:Restricted tasks Only members "
                "of the Restricted tasks group can have activities on restricted "
                "tasks. Leaving the group: Member, with activities on "
                '"Pigs Budget". Assign those activities to a member or mark them '
                "as done first."
            ],
        )

    @users("settings_test")
    def test_group_form_warns_of_activities_on_task_not_followed(self):
        # an activity makes its user follow the task, who may stop following it
        user_other = mail_new_test_user(
            self.env,
            login="other_member_test",
            name="Other Member",
            groups="project.group_project_user,"
            "project_task_restricted.group_restricted_task",
        )
        self.task_restricted.with_user(self.user_member).activity_schedule(
            "mail.mail_activity_data_todo", user_id=user_other.id
        )
        self.task_restricted.with_user(user_other).message_unsubscribe(
            partner_ids=user_other.partner_id.ids
        )
        # not saved: saving is refused
        group_form = Form(self.group.with_user(self.env.user))
        with self.assertLogs("odoo.tests.common.onchange", logging.WARNING) as logs:
            group_form.users.remove(id=user_other.id)
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.tests.common.onchange:Restricted tasks Only members "
                "of the Restricted tasks group can have activities on restricted "
                "tasks. Leaving the group: Other Member, with activities on "
                '"Pigs Budget". Assign those activities to a member or mark them '
                "as done first."
            ],
        )

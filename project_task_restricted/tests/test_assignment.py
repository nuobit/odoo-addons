# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, users

from .common import TestProjectTaskRestrictedCommon


class TestAssignment(TestProjectTaskRestrictedCommon):
    @users("member_test")
    def test_member_assigns_member_to_restricted_task(self):
        with Form(self.task_restricted.with_user(self.env.user)) as task_form:
            task_form.user_ids.add(self.user_project_sync)
        self.assertEqual(
            set(self.task_restricted.user_ids.ids),
            {self.user_member.id, self.user_project_sync.id},
        )

    @users("member_test")
    def test_member_cannot_assign_non_member_to_restricted_task(self):
        task_form = Form(self.task_restricted.with_user(self.env.user))
        task_form.user_ids.add(self.user_developer)
        with self.assertRaises(ValidationError) as error:
            task_form.save()
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can be assigned to the "
            'restricted task "Pigs Budget". Not in the group: Developer. Remove '
            "them from the assignees, or untick Restricted.",
        )

    @users("member_test")
    def test_member_cannot_mark_task_with_non_member_assignee(self):
        task_form = Form(self.task_1.with_user(self.env.user))
        task_form.restricted = True
        with self.assertRaises(ValidationError) as error:
            task_form.save()
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can be assigned to the "
            'restricted task "Pigs UserTask". Not in the group: Armande '
            "ProjectUser. Remove them from the assignees, or untick Restricted.",
        )

    # a personal stage is a row of the same table as the assignees
    @users("developer_test")
    def test_non_member_cannot_become_assignee_through_personal_stage(self):
        with self.assertRaises(ValidationError) as error:
            self.env["project.task.stage.personal"].create(
                {"task_id": self.task_restricted.id, "user_id": self.env.user.id}
            )
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can be assigned to the "
            'restricted task "Pigs Budget". Not in the group: Developer. Remove '
            "them from the assignees, or untick Restricted.",
        )

    @users("developer_test")
    def test_non_member_cannot_move_personal_stage_to_restricted_task(self):
        self.task_quote.sudo().user_ids += self.env.user
        stage = self.env["project.task.stage.personal"].search(
            [("task_id", "=", self.task_quote.id), ("user_id", "=", self.env.user.id)]
        )
        with self.assertRaises(ValidationError) as error:
            stage.write({"task_id": self.task_restricted.id})
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can be assigned to the "
            'restricted task "Pigs Budget". Not in the group: Developer. Remove '
            "them from the assignees, or untick Restricted.",
        )

    @users("project_sync_test")
    def test_member_moves_personal_stage_to_restricted_task(self):
        self.task_quote.sudo().user_ids += self.env.user
        stage = self.env["project.task.stage.personal"].search(
            [("task_id", "=", self.task_quote.id), ("user_id", "=", self.env.user.id)]
        )
        stage.write({"task_id": self.task_restricted.id})
        self.env["base"].flush()
        self.task_restricted.invalidate_cache(["user_ids"])
        self.assertIn(self.env.user, self.task_restricted.sudo().user_ids)

    @users("member_test")
    def test_member_gives_member_activity_on_restricted_task(self):
        activity = self.task_restricted.activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_project_sync.id
        )
        self.assertEqual(activity.user_id, self.user_project_sync)

    # activity_schedule creates automated activities, which Odoo does not check
    @users("member_test")
    def test_member_cannot_give_non_member_activity_on_restricted_task(self):
        with self.assertRaises(ValidationError) as error:
            self.task_restricted.activity_schedule(
                "mail.mail_activity_data_todo", user_id=self.user_developer.id
            )
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            'the restricted task "Pigs Budget". Not in the group: Developer. '
            "Assign those activities to a member, or untick Restricted.",
        )

    # Odoo checks an activity created by hand against the document too, after
    # the module's check
    @users("member_test")
    def test_member_cannot_create_non_member_activity_by_hand(self):
        with self.assertRaises(ValidationError) as error:
            self.env["mail.activity"].create(
                {
                    "res_model_id": self.env.ref("project.model_project_task").id,
                    "res_id": self.task_restricted.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "user_id": self.user_developer.id,
                }
            )
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            'the restricted task "Pigs Budget". Not in the group: Developer. '
            "Assign those activities to a member, or untick Restricted.",
        )

    @users("member_test")
    def test_member_cannot_mark_task_with_non_member_activity(self):
        self.task_quote.activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.user_developer.id
        )
        task_form = Form(self.task_quote.with_user(self.env.user))
        task_form.restricted = True
        with self.assertRaises(ValidationError) as error:
            task_form.save()
        self.assertEqual(
            str(error.exception),
            "Only members of the Restricted tasks group can have activities on "
            'the restricted task "Pigs Quote". Not in the group: Developer. '
            "Assign those activities to a member, or untick Restricted.",
        )

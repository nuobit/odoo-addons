# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, users

from .common import TestProjectTaskRestrictedCommon


class TestSubtasksCopy(TestProjectTaskRestrictedCommon):
    @users("member_test")
    def test_member_creates_subtask_of_restricted_task(self):
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id,
                default_parent_id=self.task_restricted.id,
            )
        )
        task_form.name = "Pigs Budget Detail"
        task = task_form.save()
        self.assertTrue(task.restricted)

    @users("member_test")
    def test_member_unticks_new_subtask_of_restricted_task(self):
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id,
                default_parent_id=self.task_restricted.id,
            )
        )
        task_form.name = "Pigs Budget Detail"
        task_form.restricted = False
        task = task_form.save()
        self.assertFalse(task.restricted)

    @users("member_test")
    def test_new_subtask_with_non_member_assignee_needs_unticking(self):
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id,
                default_parent_id=self.task_restricted.id,
            )
        )
        task_form.name = "Pigs Budget Detail"
        task_form.user_ids.add(self.user_developer)
        with self.assertRaises(ValidationError):
            task_form.save()
        task_form.restricted = False
        task = task_form.save()
        self.assertFalse(task.restricted)

    @users("member_test")
    def test_member_picks_restricted_parent_for_new_task(self):
        # the task form shows the parent in debug mode only
        task_form = Form(
            self.env["project.task"].with_context(
                default_project_id=self.project_pigs.id
            )
        )
        task_form.name = "Pigs Budget Detail"
        task_form.parent_id = self.task_restricted
        task = task_form.save()
        self.assertTrue(task.restricted)

    @users("member_test")
    def test_member_picks_restricted_parent_for_existing_task(self):
        # the task form shows the parent in debug mode only
        with Form(self.task_quote.with_user(self.env.user)) as task_form:
            task_form.parent_id = self.task_restricted
        self.assertFalse(self.task_quote.restricted)

    @users("member_test")
    def test_member_quick_creates_subtask_of_restricted_task(self):
        task = (
            self.env["project.task"]
            .with_context(
                default_project_id=self.project_pigs.id,
                default_parent_id=self.task_restricted.id,
            )
            .create({"name": "Pigs Budget Detail"})
        )
        self.assertTrue(task.restricted)

    @users("member_test")
    def test_member_adds_subtask_in_restricted_task_list(self):
        self.project_pigs.sudo().allow_subtasks = True
        with Form(self.task_restricted.with_user(self.env.user)) as task_form:
            with task_form.child_ids.new() as subtask_line:
                subtask_line.name = "Pigs Budget Detail"
        self.assertTrue(self.task_restricted.child_ids.restricted)

    @users("member_test")
    def test_member_creates_subtask_without_mark_value(self):
        task = self.env["project.task"].create(
            {
                "name": "Pigs Budget Detail",
                "project_id": self.project_pigs.id,
                "parent_id": self.task_restricted.id,
            }
        )
        self.assertTrue(task.restricted)

    @users("member_test")
    def test_marking_task_leaves_its_subtasks_unchanged(self):
        subtask = self.env["project.task"].create(
            {
                "name": "Pigs Quote Detail",
                "project_id": self.project_pigs.id,
                "parent_id": self.task_quote.id,
            }
        )
        self.task_quote.with_user(self.env.user).write({"restricted": True})
        self.assertFalse(subtask.restricted)
        subtask.write({"restricted": True})
        self.task_quote.with_user(self.env.user).write({"restricted": False})
        self.assertTrue(subtask.restricted)

    @users("member_test")
    def test_changing_parent_changes_no_mark(self):
        self.task_quote.with_user(self.env.user).write(
            {"parent_id": self.task_restricted.id}
        )
        self.assertFalse(self.task_quote.restricted)
        subtask = self.env["project.task"].create(
            {
                "name": "Pigs Budget Detail",
                "project_id": self.project_pigs.id,
                "parent_id": self.task_restricted.id,
            }
        )
        subtask.write({"parent_id": False})
        self.assertTrue(subtask.restricted)

    @users("member_test")
    def test_member_duplicates_restricted_task(self):
        task = self.task_restricted.with_user(self.env.user).copy()
        self.assertEqual(task.name, "Pigs Budget (copy)")
        self.assertTrue(task.restricted)

    @users("project_sync_test")
    def test_member_duplicates_project_with_restricted_task(self):
        project = self.project_pigs.with_user(self.env.user).copy()
        self.assertEqual(
            sorted((task.name, task.restricted) for task in project.task_ids),
            [
                ("Pigs Budget", True),
                ("Pigs ManagerTask", False),
                ("Pigs Quote", False),
                ("Pigs UserTask", False),
            ],
        )

    @users("administrator_test")
    def test_non_member_duplicates_project_without_restricted_task(self):
        project = self.project_pigs.with_user(self.env.user).copy()
        self.assertEqual(
            sorted(project.sudo().task_ids.mapped("name")),
            ["Pigs ManagerTask", "Pigs Quote", "Pigs UserTask"],
        )

    def test_recurring_restricted_task_repeats_marked(self):
        self.project_pigs.allow_recurring_tasks = True
        with freeze_time("2020-01-01"):
            task = (
                self.env["project.task"]
                .with_user(self.user_member)
                .create(
                    {
                        "name": "Pigs Monthly Budget",
                        "project_id": self.project_pigs.id,
                        "restricted": True,
                        "recurring_task": True,
                        "repeat_interval": 1,
                        "repeat_unit": "month",
                        "repeat_type": "forever",
                        "repeat_on_month": "date",
                        "repeat_day": "15",
                        "repeat_week": "first",
                        "repeat_weekday": "mon",
                    }
                )
            )
        with freeze_time("2020-01-15"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
        self.assertEqual(task.recurrence_id.task_ids.mapped("restricted"), [True, True])

    def test_recurring_task_copies_keep_subtask_marks(self):
        self.project_pigs.allow_recurring_tasks = True
        with freeze_time("2020-01-01"):
            task = (
                self.env["project.task"]
                .with_user(self.user_member)
                .create(
                    {
                        "name": "Pigs Monthly Report",
                        "project_id": self.project_pigs.id,
                        "recurring_task": True,
                        "repeat_interval": 1,
                        "repeat_unit": "month",
                        "repeat_type": "forever",
                        "repeat_on_month": "date",
                        "repeat_day": "15",
                        "repeat_week": "first",
                        "repeat_weekday": "mon",
                    }
                )
            )
            self.env["project.task"].with_user(self.user_member).create(
                {
                    "name": "Pigs Monthly Prices",
                    "project_id": self.project_pigs.id,
                    "parent_id": task.id,
                    "restricted": True,
                }
            )
        with freeze_time("2020-01-15"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
        occurrence = (task.recurrence_id.task_ids - task).filtered(
            lambda occurrence: not occurrence.parent_id
        )
        self.assertFalse(occurrence.restricted)
        self.assertEqual(occurrence.child_ids.mapped("restricted"), [True])

    def test_recurring_restricted_task_copies_keep_unticked_subtask(self):
        self.project_pigs.allow_recurring_tasks = True
        with freeze_time("2020-01-01"):
            task = (
                self.env["project.task"]
                .with_user(self.user_member)
                .create(
                    {
                        "name": "Pigs Monthly Budget",
                        "project_id": self.project_pigs.id,
                        "restricted": True,
                        "recurring_task": True,
                        "repeat_interval": 1,
                        "repeat_unit": "month",
                        "repeat_type": "forever",
                        "repeat_on_month": "date",
                        "repeat_day": "15",
                        "repeat_week": "first",
                        "repeat_weekday": "mon",
                    }
                )
            )
            self.env["project.task"].with_user(self.user_member).create(
                [
                    {
                        "name": "Pigs Monthly Prices",
                        "project_id": self.project_pigs.id,
                        "parent_id": task.id,
                    },
                    {
                        "name": "Pigs Monthly Notes",
                        "project_id": self.project_pigs.id,
                        "parent_id": task.id,
                        "restricted": False,
                    },
                ]
            )
        with freeze_time("2020-01-15"):
            self.env["project.task.recurrence"]._cron_create_recurring_tasks()
        occurrence = (task.recurrence_id.task_ids - task).filtered(
            lambda occurrence: not occurrence.parent_id
        )
        self.assertEqual(
            sorted(
                occurrence.child_ids.mapped(
                    lambda child: (child.name, child.restricted)
                )
            ),
            [("Pigs Monthly Notes", False), ("Pigs Monthly Prices", True)],
        )

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import users

from odoo.addons.project_task_restricted.tests.common import (
    TestProjectTaskRestrictedCommon,
)


# a project manager sees every timesheet line of the projects; the lines live
# in their own project: deleting Pigs, the inherited core test expects the
# error about its tasks, and timesheets on Pigs would raise hr_timesheet's
# warning about them instead
class TestTimesheet(TestProjectTaskRestrictedCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_hours = cls.env["project.project"].create(
            {"name": "Hours", "privacy_visibility": "employees"}
        )
        Task = (
            cls.env["project.task"]
            .with_user(cls.user_member)
            .with_context(mail_create_nolog=True)
        )
        task_budget = Task.create(
            {
                "name": "Hours Budget",
                "project_id": cls.project_hours.id,
                "restricted": True,
            }
        )
        task_quote = Task.create(
            {"name": "Hours Quote", "project_id": cls.project_hours.id}
        )
        employee = cls.env["hr.employee"].create(
            {"name": "Member", "user_id": cls.user_member.id}
        )
        cls.env["account.analytic.line"].create(
            [
                {
                    "name": "Budget figures",
                    "project_id": cls.project_hours.id,
                    "task_id": task_budget.id,
                    "employee_id": employee.id,
                    "unit_amount": 2,
                },
                {
                    "name": "Quote figures",
                    "project_id": cls.project_hours.id,
                    "task_id": task_quote.id,
                    "employee_id": employee.id,
                    "unit_amount": 1,
                },
                {
                    "name": "Project review",
                    "project_id": cls.project_hours.id,
                    "employee_id": employee.id,
                    "unit_amount": 1,
                },
            ]
        )

    @users("administrator_test")
    def test_non_member_sees_no_timesheet_of_restricted_task(self):
        lines = self.env["account.analytic.line"].search(
            [("project_id", "=", self.project_hours.id)]
        )
        self.assertEqual(
            sorted(lines.mapped("name")), ["Project review", "Quote figures"]
        )

    def test_non_member_total_counts_no_restricted_task_hours(self):
        self.user_administrator.groups_id += self.env.ref(
            "hr_timesheet.group_hr_timesheet_approver"
        )
        self.assertEqual(
            self.project_hours.with_user(self.user_administrator).total_timesheet_time,
            2,
        )

    def test_member_total_counts_every_hour(self):
        self.user_project_sync.groups_id += self.env.ref(
            "hr_timesheet.group_hr_timesheet_approver"
        )
        self.assertEqual(
            self.project_hours.with_user(self.user_project_sync).total_timesheet_time,
            4,
        )

    @users("project_sync_test")
    def test_member_sees_every_timesheet(self):
        lines = self.env["account.analytic.line"].search(
            [("project_id", "=", self.project_hours.id)]
        )
        self.assertEqual(
            sorted(lines.mapped("name")),
            ["Budget figures", "Project review", "Quote figures"],
        )

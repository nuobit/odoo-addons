# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.project_task_restricted.tests.common import (
    TestProjectTaskRestrictedCommon,
)


# the timesheet portal reads the lines as superuser, with a domain of its own
# for the users outside the Timesheets groups
@tagged("post_install", "-at_install")
class TestPortal(TestProjectTaskRestrictedCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_portal = mail_new_test_user(
            cls.env, login="portal_test", name="Customer", groups="base.group_portal"
        )
        project = cls.env["project.project"].create(
            {"name": "Shared", "privacy_visibility": "portal"}
        )
        project.message_subscribe(partner_ids=cls.user_portal.partner_id.ids)
        Task = (
            cls.env["project.task"]
            .with_user(cls.user_member)
            .with_context(mail_create_nolog=True)
        )
        cls.task_review = Task.create(
            {"name": "Shared Review", "project_id": project.id}
        )
        task_budget = Task.create(
            {
                "name": "Shared Budget",
                "project_id": project.id,
                "parent_id": cls.task_review.id,
                "restricted": True,
            }
        )
        employee = cls.env["hr.employee"].create(
            {"name": "Member", "user_id": cls.user_member.id}
        )
        cls.env["account.analytic.line"].create(
            [
                {
                    "name": "Budget figures",
                    "project_id": project.id,
                    "task_id": task_budget.id,
                    "employee_id": employee.id,
                    "unit_amount": 2,
                },
                {
                    "name": "Review notes",
                    "project_id": project.id,
                    "task_id": cls.task_review.id,
                    "employee_id": employee.id,
                    "unit_amount": 1,
                },
            ]
        )

    def test_portal_timesheets_list_no_restricted_task_line(self):
        self.authenticate("portal_test", "portal_test")
        response = self.url_open("/my/timesheets")
        self.assertIn("Review notes", response.text)
        self.assertNotIn("Budget figures", response.text)

    # the task page adds up the hours of the task's subtasks
    def test_portal_task_page_counts_no_restricted_subtask_hours(self):
        self.authenticate("portal_test", "portal_test")
        response = self.url_open("/my/task/%s" % self.task_review.id)
        self.assertIn("Review notes", response.text)
        self.assertNotIn("Hours recorded on sub-tasks", response.text)

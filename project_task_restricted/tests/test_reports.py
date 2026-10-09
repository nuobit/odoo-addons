# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import users

from .common import TestProjectTaskRestrictedCommon


# both reports are views over the task table, outside the task's own rule
class TestReports(TestProjectTaskRestrictedCommon):
    @users("administrator_test")
    def test_task_analysis_lists_no_restricted_task_to_non_member(self):
        rows = self.env["report.project.task.user"].search(
            [("project_id", "=", self.project_pigs.id)]
        )
        self.assertEqual(
            sorted(rows.mapped("name")),
            ["Pigs ManagerTask", "Pigs Quote", "Pigs UserTask"],
        )

    @users("administrator_test")
    def test_task_analysis_counts_no_restricted_task_for_non_member(self):
        groups = self.env["report.project.task.user"].read_group(
            [("project_id", "=", self.project_pigs.id)], ["nbr"], ["project_id"]
        )
        self.assertEqual([group["nbr"] for group in groups], [3])

    @users("project_sync_test")
    def test_task_analysis_lists_restricted_task_to_member(self):
        rows = self.env["report.project.task.user"].search(
            [("project_id", "=", self.project_pigs.id)]
        )
        self.assertEqual(
            sorted(rows.mapped("name")),
            ["Pigs Budget", "Pigs ManagerTask", "Pigs Quote", "Pigs UserTask"],
        )

    @users("administrator_test")
    def test_burndown_counts_no_restricted_task_for_non_member(self):
        groups = self.env["project.task.burndown.chart.report"].read_group(
            [("project_id", "=", self.project_pigs.id)], ["nb_tasks"], ["date:month"]
        )
        self.assertEqual([group["nb_tasks"] for group in groups], [3])

    @users("project_sync_test")
    def test_burndown_counts_restricted_task_for_member(self):
        groups = self.env["project.task.burndown.chart.report"].read_group(
            [("project_id", "=", self.project_pigs.id)], ["nb_tasks"], ["date:month"]
        )
        self.assertEqual([group["nb_tasks"] for group in groups], [4])

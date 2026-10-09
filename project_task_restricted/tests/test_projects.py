# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import users

from .common import TestProjectTaskRestrictedCommon


# Odoo archives, and counts before deleting, only the tasks the user can read
class TestProjects(TestProjectTaskRestrictedCommon):
    @users("administrator_test")
    def test_non_member_archiving_project_archives_restricted_task(self):
        self.project_pigs.with_user(self.env.user).write({"active": False})
        self.assertFalse(self.task_restricted.sudo().active)

    @users("administrator_test")
    def test_non_member_restoring_project_restores_restricted_task(self):
        self.project_pigs.sudo().write({"active": False})
        # the project's tasks read as superuser stay in the cache for every
        # user of the transaction; a request starts without them
        self.project_pigs.invalidate_cache(["tasks"])
        self.project_pigs.with_user(self.env.user).write({"active": True})
        self.assertTrue(self.task_restricted.sudo().active)

    @users("administrator_test")
    def test_non_member_cannot_delete_project_with_only_restricted_tasks(self):
        project = self.env["project.project"].create({"name": "Budgets"})
        self.env["project.task"].with_user(self.user_member).create(
            {"name": "Budgets Pricing", "project_id": project.id, "restricted": True}
        )
        with self.assertRaises(UserError):
            project.unlink()
        self.assertTrue(project.exists())

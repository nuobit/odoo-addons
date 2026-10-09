# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.project.tests.test_project_base import TestProjectCommon


class TestProjectTaskRestrictedCommon(TestProjectCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_member = mail_new_test_user(
            cls.env,
            login="member_test",
            name="Member",
            groups="project.group_project_user,"
            "project_task_restricted.group_restricted_task",
        )
        cls.user_developer = mail_new_test_user(
            cls.env,
            login="developer_test",
            name="Developer",
            groups="project.group_project_user",
        )
        cls.user_administrator = mail_new_test_user(
            cls.env,
            login="administrator_test",
            name="Administrator",
            groups="project.group_project_manager",
        )
        cls.user_project_sync = mail_new_test_user(
            cls.env,
            login="project_sync_test",
            name="Project Sync",
            groups="project.group_project_manager,"
            "project_task_restricted.group_restricted_task",
        )
        cls.task_restricted = (
            cls.env["project.task"]
            .with_user(cls.user_member)
            .with_context(mail_create_nolog=True)
            .create(
                {
                    "name": "Pigs Budget",
                    "project_id": cls.project_pigs.id,
                    "restricted": True,
                }
            )
        )
        cls.task_quote = (
            cls.env["project.task"]
            .with_user(cls.user_member)
            .with_context(mail_create_nolog=True)
            .create({"name": "Pigs Quote", "project_id": cls.project_pigs.id})
        )

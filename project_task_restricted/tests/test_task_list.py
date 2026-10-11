# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import users

from .common import TestProjectTaskRestrictedCommon


class TestTaskList(TestProjectTaskRestrictedCommon):
    @users("member_test")
    def test_member_list_has_restricted_column_hidden_by_default(self):
        view = self.env["project.task"].fields_view_get(
            view_id=self.env.ref("project.view_task_tree2").id, view_type="tree"
        )
        (column,) = etree.fromstring(view["arch"]).xpath("//field[@name='restricted']")
        self.assertIn("restricted", view["fields"])
        self.assertEqual(column.get("optional"), "hide")

    @users("developer_test")
    def test_non_member_list_has_no_restricted_column(self):
        view = self.env["project.task"].fields_view_get(
            view_id=self.env.ref("project.view_task_tree2").id, view_type="tree"
        )
        self.assertFalse(
            etree.fromstring(view["arch"]).xpath("//field[@name='restricted']")
        )
        self.assertNotIn("restricted", view["fields"])

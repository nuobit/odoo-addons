# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.tests.common import users

from .common import TestProjectTaskRestrictedCommon


class TestKanban(TestProjectTaskRestrictedCommon):
    @users("member_test")
    def test_member_kanban_marks_restricted_cards(self):
        view = self.env["project.task"].fields_view_get(
            view_id=self.env.ref("project.view_task_kanban").id, view_type="kanban"
        )
        (marker,) = etree.fromstring(view["arch"]).xpath("//span[@name='restricted']")
        self.assertIn("restricted", view["fields"])
        self.assertEqual(marker.get("class"), "badge badge-danger")
        self.assertEqual(marker.text, "Restricted")
        self.assertEqual(
            json.loads(marker.get("modifiers", "{}")),
            {"invisible": [["restricted", "=", False]]},
        )

    @users("developer_test")
    def test_non_member_kanban_has_no_restricted_field(self):
        view = self.env["project.task"].fields_view_get(
            view_id=self.env.ref("project.view_task_kanban").id, view_type="kanban"
        )
        (marker,) = etree.fromstring(view["arch"]).xpath("//span[@name='restricted']")
        self.assertNotIn("restricted", view["fields"])
        self.assertEqual(json.loads(marker.get("modifiers", "{}")), {"invisible": True})

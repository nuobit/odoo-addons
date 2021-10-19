# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestTaskAutoassign(TransactionCase):
    def setUp(self):
        super(TestTaskAutoassign, self).setUp()

    def test_task_autoassign(self):
        product1 = self.env.ref(
            "sale_timesheet.product_service_order_timesheet_product_template"
        )
        product1.service_time = 1
        product2 = self.env["product.template"].create(
            {
                "name": "Service1",
                "type": "service",
                "service_tracking": "task_global_project",
                "project_id": self.env.ref("sale_timesheet.project_support").id,
            }
        )
        product2.service_time = 3
        self.env["project.task"].create(
            {
                "name": "Task1",
                "project_id": self.env.ref("sale_timesheet.project_support").id,
                "user_id": self.env.ref("base.user_demo").id,
                "date_start": datetime.datetime(2020, 11, 22, 21, 30, 0),
                "date_end": datetime.datetime(2020, 11, 22, 22, 30, 0),
            }
        )
        order1 = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_12").id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product1.product_variant_id.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": product2.product_variant_id.id,
                        },
                    ),
                ],
            }
        )
        order1.action_confirm()

    def test_change_stage_on_sale_order_when_bike_location_is_changed(self):
        """
        PRE:
            - project1 exists
            - project1 has stage1 (bring_in) and stage2 (in_place)
            - product1 exists and is assigned to project1
            - partner1 exists
            - saleorder1 exists
            - saleorder1 has partner1 and product1
            - saleorder1 has bike_location 'bring_in'
            - saleorder1 is confirmed
        ACT:
            - change bike_location to 'in_shop'
        POST:
            - all tasks have their stage as 'in_place'
        """
        # ARRANGE:
        project1 = self.env["project.project"].create(
            {
                "name": "project1",
                "type_ids": [
                    (0, False, {"name": "stage1", "meta_type": "bring_in"}),
                    (0, False, {"name": "stage2", "meta_type": "in_place"}),
                ],
            }
        )
        product1 = self.env["product.product"].create(
            {
                "name": "product1",
                "type": "service",
                "service_tracking": "task_global_project",
                "project_id": project1.id,
            }
        )
        partner1 = self.env["res.partner"].create(
            {
                "name": "partner1",
            }
        )
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product1.id,
                        },
                    )
                ],
            }
        )
        saleorder1.action_confirm()

        # ACT
        saleorder1.bike_location = "in_shop"

        # ASSERT
        self.assertEqual(
            saleorder1.tasks_ids.mapped("stage_id.meta_type"),
            ["in_place"],
            "Expected 'In place', other result found",
        )

    def test_change_stage_on_sale_order_when_bike_location_is_na(self):
        """
        PRE:
            - project1 exists
            - project1 has stage1 (bring_in) and stage2 (done)
            - product1 exists and is assigned to project1
            - partner1 exists
            - saleorder1 exists
            - saleorder1 has partner1 and product1
            - saleorder1 has bike_location 'bring_in'
            - saleorder1 is confirmed
        ACT:
            - change bike_location to 'na'
        POST:
            - Raise User Error, changes can't be applied
        """
        # ARRANGE:
        project1 = self.env["project.project"].create(
            {
                "name": "project1",
                "type_ids": [
                    (0, False, {"name": "stage1", "meta_type": "bring_in"}),
                    (0, False, {"name": "stage2", "meta_type": "done"}),
                ],
            }
        )
        product1 = self.env["product.product"].create(
            {
                "name": "product1",
                "type": "service",
                "service_tracking": "task_global_project",
                "project_id": project1.id,
            }
        )
        partner1 = self.env["res.partner"].create(
            {
                "name": "partner1",
            }
        )
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product1.id,
                        },
                    )
                ],
            }
        )
        saleorder1.action_confirm()
        stage1 = saleorder1.tasks_ids.stage_id

        # ACT
        saleorder1.bike_location = "na"

        # ASSERT
        self.assertEqual(
            stage1, saleorder1.tasks_ids.stage_id, "Stage have changed ant it shouldn't"
        )

    def test_change_stage_on_sale_order_when_meta_type_dont_exist(self):
        """
        PRE:
            - project1 exists
            - project1 has stage1 (bring_in) and stage2 (False meta_type)
            - product1 exists and is assigned to project1
            - partner1 exists
            - saleorder1 exists
            - saleorder1 has partner1 and product1
            - saleorder1 has bike_location 'stage1'
            - saleorder1 is confirmed
        ACT:
            - change bike_location to 'in_shop'
        POST:
            - Raise ValidationError, theres no stages without meta_type
        """
        # ARRANGE:
        project1 = self.env["project.project"].create(
            {
                "name": "project1",
                "type_ids": [
                    (0, False, {"name": "stage1", "meta_type": "bring_in"}),
                    (0, False, {"name": "stage2", "meta_type": False}),
                ],
            }
        )
        product1 = self.env["product.product"].create(
            {
                "name": "product1",
                "type": "service",
                "service_tracking": "task_global_project",
                "project_id": project1.id,
            }
        )
        partner1 = self.env["res.partner"].create(
            {
                "name": "partner1",
            }
        )
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product1.id,
                        },
                    )
                ],
            }
        )
        saleorder1.action_confirm()

        # ACT & ASSERT
        try:
            with self.assertRaises(ValidationError):
                saleorder1.bike_location = "in_shop"
        except AssertionError:
            self.fail("This test should fail with an UserError but it works correctly")

    def test_change_stage_on_task_when_bike_location_is_changed_and_first_stage_is_done(
        self,
    ):
        """
        PRE:
            - stage1 exists
            - project1 exists
            - project1 has stage1 (done) and stage2 (bring_in)
            - product1 exists and is assigned to project1
            - partner1 exists
            - saleorder1 exists
            - saleorder1 has partner1 and product1
            - saleorder1 has bike_location 'bring_in'
            - saleorder1 is confirmed
            - task from saleorder1 is in stage1
        ACT:
            - change bike_location to 'bring_in'
        POST:
            - the task continues in stage1
        """
        # ARRANGE:
        stage1 = self.env["project.task.type"].create(
            {"name": "stage1", "meta_type": "done"}
        )
        project1 = self.env["project.project"].create(
            {
                "name": "project1",
                "type_ids": [
                    (4, stage1.id, False),
                    (0, False, {"name": "stage2", "meta_type": "bring_in"}),
                ],
            }
        )
        product1 = self.env["product.product"].create(
            {
                "name": "product1",
                "type": "service",
                "service_tracking": "task_global_project",
                "project_id": project1.id,
            }
        )
        partner1 = self.env["res.partner"].create(
            {
                "name": "partner1",
            }
        )
        saleorder1 = self.env["sale.order"].create(
            {
                "partner_id": partner1.id,
                "bike_location": "bring_in",
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product1.id,
                        },
                    )
                ],
            }
        )
        saleorder1.action_confirm()
        saleorder1.tasks_ids.stage_id = stage1

        # ACT
        saleorder1.bike_location = "bring_in"

        # ASSERT
        self.assertEqual(
            saleorder1.tasks_ids.stage_id,
            stage1,
            "Expected 'In place', other result found",
        )

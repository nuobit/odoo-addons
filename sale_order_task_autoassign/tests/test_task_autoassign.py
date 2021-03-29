# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import datetime

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

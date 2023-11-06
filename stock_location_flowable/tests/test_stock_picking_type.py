# Copyright NuoBiT Solutions - Frank Cespedes <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import ValidationError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockPickingType(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingType, cls).setUpClass()

    def test_unique_flowable_operation_picking_type(self):
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        # ACT
        with self.assertRaises(ValidationError) as error:
            self.picking_type_mrp_operation_1_2 = self.env["stock.picking.type"].create(
                {
                    "name": "Production2 2",
                    "sequence_code": "SEQ-MRP 2",
                    "code": "mrp_operation",
                    "flowable_operation": True,
                }
            )

        # ASSERT
        msg_error = "Only one picking type can be flowable in a warehouse %s."
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

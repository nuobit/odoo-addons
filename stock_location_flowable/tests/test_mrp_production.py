# Copyright NuoBiT Solutions - Frank Cespedes <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestMrpProduction(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestMrpProduction, cls).setUpClass()

    def test_blocked_flowable_mrp_operation(self):
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        # ACT
        self.incoming_picking.button_validate()

        # ASSERT
        self.assertTrue(self.incoming_picking.location_dest_id.flowable_blocked)

    def test_block_new_production_flowable_location_by_outgoing_picking(self):
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        # ACT
        with self.assertRaises(UserError) as error:
            self.outgoing_picking.button_validate()

        # ASSERT
        msg_error = (
            "The location %s is blocked. Probably you need to review"
            " the pending manufacturing orders related to this location"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

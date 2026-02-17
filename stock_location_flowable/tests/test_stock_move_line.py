# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockMoveLine(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveLine, cls).setUpClass()

    def test_blocked_location_rejects_unrelated_production_done(self):
        """
        Test that validating a picking whose destination is a blocked
        flowable location raises an error.

        PRE:    - A flowable location blocked by a production
        ACT:    - Try to validate an outgoing picking targeting that location
        POST:   - An error is raised about the location being blocked
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        # Location should now be blocked by the flowable production
        self.assertTrue(self.location_flowable_1.flowable_blocked)

        # ACT & ASSERT
        with self.assertRaises(Exception) as error:
            self.outgoing_picking.button_validate()

        msg_error = (
            "The location %s is blocked. Probably you need to review"
            " the pending manufacturing orders related to this location"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockMove(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()

    def test_modify_in_progress_flowable_move_raises_error(self):
        """
        Test that cancelling a flowable production with a picking triggers
        the stock.move write guard, which prevents state changes on raw
        moves of an in-progress mixing.

        When a user clicks "Cancel" on the MO, the cancel flow attempts to
        change the raw moves' state, and the write override blocks it.

        PRE:    - A flowable MO in to_close state with a picking
        ACT:    - Cancel the production (user action)
        POST:   - UserError is raised about mixing in progress
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", self.location_flowable_1.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(production.picking_id)
        self.assertEqual(production.state, "to_close")

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            production.action_cancel()

        msg_error = (
            "You cannot modify a production with a picking associated."
            " The mixing is in progress."
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

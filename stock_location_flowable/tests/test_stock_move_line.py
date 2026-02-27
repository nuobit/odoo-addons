# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import ValidationError

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

    def test_blocked_location_rejects_incoming_reception(self):
        """
        Test that a second PO reception to a blocked flowable location
        is rejected even though the reception is not part of any MO.

        PRE:    - A flowable location blocked by a production (from a first reception)
                - A second incoming picking prepared before the location was blocked
        ACT:    - Try to validate the second incoming picking
        POST:   - A ValidationError is raised about the location being blocked
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_2 = self.env["stock.production.lot"].create(
            {
                "name": "Lot2",
                "product_id": self.product_flowable_1.id,
            }
        )
        second_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": second_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_2.id,
                "qty_done": 10,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )

        # Block the location by validating the first reception
        self.incoming_picking.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)

        # ACT & ASSERT
        with self.assertRaises(ValidationError) as error:
            second_picking.button_validate()

        msg_error = (
            "The location %s is blocked. Probably you need to review"
            " the pending manufacturing orders related to this location"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_blocked_location_rejects_internal_transfer(self):
        """
        Test that an internal transfer from a blocked flowable location
        is rejected.

        PRE:    - A flowable location blocked by a production
                - An internal transfer prepared before the location was blocked
        ACT:    - Try to validate the internal transfer
        POST:   - An error is raised about the location being blocked
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_2 = self.env["stock.production.lot"].create(
            {
                "name": "LotInternal",
                "product_id": self.product_flowable_1.id,
            }
        )
        transfer_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_internal_1.id,
                "location_id": self.location_flowable_1.id,
                "location_dest_id": self.location_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": transfer_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_2.id,
                "qty_done": 5,
                "location_id": self.location_flowable_1.id,
                "location_dest_id": self.location_1.id,
                "company_id": self.env.company.id,
            }
        )

        # Block the location by validating the first reception
        self.incoming_picking.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)

        # ACT & ASSERT
        with self.assertRaises(Exception) as error:
            transfer_picking.button_validate()

        msg_error = (
            "The location %s is blocked. Probably you need to review"
            " the pending manufacturing orders related to this location"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockReturnPicking(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockReturnPicking, cls).setUpClass()

    def test_return_from_flowable_location_raises_error(self):
        """
        Test that returning a product that was delivered to a flowable
        location is blocked.

        PRE:    - A completed incoming picking to a flowable location
        ACT:    - Attempt to create a return for that picking
        POST:   - UserError is raised
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot = self._create_lot(self.product_flowable_1, "TEST-RETURN-LOT")
        picking = self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot, 50
        )

        # ACT
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_model="stock.picking",
            )
            .create(
                {
                    "picking_id": picking.id,
                    "location_id": self.supplier_location.id,
                }
            )
        )
        return_wizard._onchange_picking_id()

        with self.assertRaises(UserError) as error:
            return_wizard._create_returns()

        # ASSERT
        msg_error = (
            "You cannot return the following products because"
            " they come from a flowable location: %s"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_return_from_non_flowable_location_succeeds(self):
        """
        Test that returning a product that was delivered to a non-flowable
        location is allowed.

        PRE:    - A completed incoming picking to a non-flowable location
        ACT:    - Create a return for that picking
        POST:   - Return picking is created successfully
        """
        # ARRANGE
        lot = self._create_lot(self.product_flowable_1, "TEST-RETURN-NOFLO")

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location_1.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product_flowable_1.name,
                "product_id": self.product_flowable_1.id,
                "product_uom_qty": 50,
                "product_uom": self.product_flowable_1.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location_1.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move.move_line_ids.write(
            {
                "qty_done": 50,
                "lot_id": lot.id,
            }
        )
        picking.button_validate()

        # ACT
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_model="stock.picking",
            )
            .create(
                {
                    "picking_id": picking.id,
                    "location_id": self.supplier_location.id,
                }
            )
        )
        return_wizard._onchange_picking_id()
        new_picking_id, pick_type_id = return_wizard._create_returns()

        # ASSERT
        self.assertTrue(new_picking_id)
        return_picking = self.env["stock.picking"].browse(new_picking_id)
        self.assertEqual(return_picking.state, "assigned")

    def test_return_from_mixed_flowable_non_flowable_picking(self):
        """
        Test that returning from a picking that delivered to both a flowable
        and a non-flowable location only blocks the return of the flowable
        product.

        PRE:    - A completed incoming picking with:
                  - Line 1: product to flowable location (MO completed)
                  - Line 2: product to non-flowable location
        ACT:    - Attempt to return the flowable product
        POST:   - UserError about the flowable product
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_flow = self._create_lot(self.product_flowable_1, "RET-MIXED-FLOW")
        lot_nonflow = self._create_lot(self.product_flowable_1, "RET-MIXED-NOFLOW")

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        # Line 1 → flowable location
        move_flow = self.env["stock.move"].create(
            {
                "name": "Flowable line",
                "picking_id": picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom": self.product_flowable_1.uom_id.id,
                "product_uom_qty": 50,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        # Line 2 → non-flowable location
        move_nonflow = self.env["stock.move"].create(
            {
                "name": "Non-flowable line",
                "picking_id": picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom": self.product_flowable_1.uom_id.id,
                "product_uom_qty": 30,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location_1.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()

        for move, lot, qty in [
            (move_flow, lot_flow, 50),
            (move_nonflow, lot_nonflow, 30),
        ]:
            ml = move.move_line_ids
            if ml:
                ml.write({"lot_id": lot.id, "qty_done": qty})
            else:
                self.env["stock.move.line"].create(
                    {
                        "picking_id": picking.id,
                        "move_id": move.id,
                        "product_id": self.product_flowable_1.id,
                        "product_uom_id": self.product_flowable_1.uom_id.id,
                        "lot_id": lot.id,
                        "qty_done": qty,
                        "location_id": self.supplier_location.id,
                        "location_dest_id": move.location_dest_id.id,
                        "company_id": self.env.company.id,
                    }
                )

        picking.button_validate()

        # Complete the MO so the location is unblocked
        production = self._find_flowable_production(self.location_flowable_1)
        if production:
            production.button_mark_done()

        # ACT — try to return both products
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_model="stock.picking",
            )
            .create(
                {
                    "picking_id": picking.id,
                    "location_id": self.supplier_location.id,
                }
            )
        )
        return_wizard._onchange_picking_id()

        # ASSERT — error mentions the flowable product
        with self.assertRaises(UserError) as error:
            return_wizard._create_returns()

        msg_error = (
            "You cannot return the following products because"
            " they come from a flowable location: %s"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

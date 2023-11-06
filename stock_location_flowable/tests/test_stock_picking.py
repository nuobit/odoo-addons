# Copyright NuoBiT Solutions - Frank Cespedes <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockPicking(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()

        cls.incoming_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_incoming_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_1.id,
            }
        )

        cls.outgoing_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_outgoing_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_1.id,
            }
        )

        cls.internal_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_internal_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_2.id,
            }
        )

        cls.mrp_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_mrp_operation_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_2.id,
            }
        )

    def test_receiving_one_product_in_flowable_location_incoming_picking(self):
        """
        Test to ensure that receiving more than one product in a flowable location
        raises an error.

        PRE:    - A picking with multiple lines directed to a flowable location
        ACT:    - Try to validate the picking
        POST:   - UserError is raised stating that only one product can be received
                at a flowable location
        """
        # ARRANGE
        moves1 = self.env["stock.move"].create(
            {
                "name": self.product_flowable_1.name,
                "product_id": self.product_flowable_1.id,
                "product_uom_qty": 5,
                "product_uom": self.product_flowable_1.uom_id.id,
                "picking_id": self.incoming_picking.id,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        moves2 = self.env["stock.move"].create(
            {
                "name": self.product_flowable_2.name,
                "product_id": self.product_flowable_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_flowable_2.uom_id.id,
                "picking_id": self.incoming_picking.id,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.action_confirm()

        lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "TEST LMP-0001",
                "product_id": self.product_flowable_1.id,
            }
        )

        lot_ch4 = self.env["stock.production.lot"].create(
            {
                "name": "TEST LMP-0002",
                "product_id": self.product_flowable_2.id,
            }
        )

        self.incoming_picking.move_line_ids = self.env["stock.move.line"].create(
            {
                "move_id": moves1.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 5,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.move_line_ids |= self.env["stock.move.line"].create(
            {
                "move_id": moves2.id,
                "product_id": self.product_flowable_2.id,
                "product_uom_id": self.product_flowable_2.uom_id.id,
                "lot_id": lot_ch4.id,
                "qty_done": 10,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        # ACT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        # ASSERT
        msg_error = (
            "You can only receive one product at location %s"
            " because a manufacturing order must be generated"
            " and the location will be blocked. Create a "
            "partial delivery for this product %s."
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_only_allowed_product_in_incoming_picking(self):
        # ARRANGE
        product_zanahoria = self.env["product.product"].create(
            {
                "name": "Zanahoria",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
            }
        )

        moves1 = self.env["stock.move"].create(
            {
                "name": product_zanahoria.name,
                "product_id": product_zanahoria.id,
                "product_uom_qty": 5,
                "product_uom": product_zanahoria.uom_id.id,
                "picking_id": self.incoming_picking.id,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.action_confirm()

        lot_zanahoria = self.env["stock.production.lot"].create(
            {
                "name": "TEST COD-0001",
                "product_id": product_zanahoria.id,
            }
        )

        self.incoming_picking.move_line_ids = self.env["stock.move.line"].create(
            {
                "move_id": moves1.id,
                "product_id": product_zanahoria.id,
                "product_uom_id": product_zanahoria.uom_id.id,
                "lot_id": lot_zanahoria.id,
                "qty_done": 5,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        # ACT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        # ASSERT
        msg_error = "Product %s not allowed in flowable location %s"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_different_uom_allowed_product_in_incoming_picking(self):
        # ARRANGE
        product_zanahoria = self.env["product.product"].create(
            {
                "name": "Zanahoria",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_litre").id,
                "uom_po_id": self.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )

        self.location_flowable_1.flowable_allowed_product_ids = [
            (4, product_zanahoria.id)
        ]

        product_zanahoria.write(
            {
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        moves1 = self.env["stock.move"].create(
            {
                "name": product_zanahoria.name,
                "product_id": product_zanahoria.id,
                "product_uom_qty": 5,
                "product_uom": product_zanahoria.uom_id.id,
                "picking_id": self.incoming_picking.id,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.action_confirm()

        lot_zanahoria = self.env["stock.production.lot"].create(
            {
                "name": "TEST COD-0001",
                "product_id": product_zanahoria.id,
            }
        )

        self.incoming_picking.move_line_ids = self.env["stock.move.line"].create(
            {
                "move_id": moves1.id,
                "product_id": product_zanahoria.id,
                "product_uom_id": product_zanahoria.uom_id.id,
                "lot_id": lot_zanahoria.id,
                "qty_done": 5,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        # ACT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        # ASSERT
        msg_error = (
            "The allowed products %s cannot have different Unit of Measure"
            " than flowable location %s"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_not_found_manufacturing_picking_type_incoming_picking(self):
        # ARRANGE
        moves = self.env["stock.move"].create(
            {
                "name": self.product_flowable_1.name,
                "product_id": self.product_flowable_1.id,
                "product_uom_qty": 10,
                "product_uom": self.product_flowable_1.uom_id.id,
                "picking_id": self.incoming_picking.id,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.action_confirm()

        lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "TEST LMP-0001",
                "product_id": self.product_flowable_1.id,
            }
        )

        self.incoming_picking.move_line_ids = self.env["stock.move.line"].create(
            {
                "move_id": moves.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.incoming_picking.location_id.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
            }
        )

        self.incoming_picking.action_assign()

        # ACT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        # ASSERT
        msg_error = (
            "Not found manufacturing picking type for flowable"
            " location %s to do flowable mixing in %s"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_successfull_picking_type_incoming_picking(self):
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "TEST LMP-0001",
                "product_id": self.product_flowable_1.id,
            }
        )

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )

        self.incoming_picking.action_confirm()

        # ACT & ASSERT
        self.incoming_picking.button_validate()

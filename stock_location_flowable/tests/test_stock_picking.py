# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
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
        self.picking_type_mrp_operation_1.flowable_operation = True

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

        lot_1 = self._create_lot(self.product_flowable_1, "TEST LMP-0001")

        lot_ch4 = self._create_lot(self.product_flowable_2, "TEST LMP-0002")

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
        self.picking_type_mrp_operation_1.flowable_operation = True

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

        lot_zanahoria = self._create_lot(product_zanahoria, "TEST COD-0001")

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
        self.picking_type_mrp_operation_1.flowable_operation = True

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

        lot_zanahoria = self._create_lot(product_zanahoria, "TEST COD-0001")

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

        lot_1 = self._create_lot(self.product_flowable_1, "TEST LMP-0001")

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
        msg_error = "Not found flowable manufacturing picking type in warehouse %s"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_more_than_one_manufacturing_picking_type_incoming_picking(self):
        """
        Test that having more than one flowable manufacturing picking type
        in the same warehouse raises an error during picking validation.

        PRE:    - Two flowable mrp_operation picking types in the same warehouse
                  (second one created bypassing the ORM constraint via SQL)
        ACT:    - Validate a picking to a flowable location
        POST:   - UserError is raised about duplicate picking types
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        picking_type_mrp_operation_2 = self.env["stock.picking.type"].create(
            {
                "name": "Production2",
                "sequence_code": "SEQ-MRP2",
                "code": "mrp_operation",
                "warehouse_id": self.picking_type_mrp_operation_1.warehouse_id.id,
            }
        )
        # Bypass the ORM constraint to simulate data inconsistency
        self.env.cr.execute(
            "UPDATE stock_picking_type SET flowable_operation = TRUE WHERE id = %s",
            (picking_type_mrp_operation_2.id,),
        )
        picking_type_mrp_operation_2.invalidate_cache()

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-DUP-LOT")

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        msg_error = "More than one flowable manufacturing picking type in warehouse %s"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_successfull_picking_type_incoming_picking(self):
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST LMP-0001")

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )

        self.incoming_picking.action_confirm()

        # ACT & ASSERT
        self.incoming_picking.button_validate()

    def test_action_view_mrp_production_single(self):
        """
        Test that action_view_mrp_production returns a form view when there
        is exactly one production linked to the picking.

        PRE:    - A picking with one flowable production
        ACT:    - Call action_view_mrp_production
        POST:   - Action opens the form view with the production res_id
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-ACTION-LOT")

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )
        self.incoming_picking.button_validate()

        # ACT
        action = self.incoming_picking.action_view_mrp_production()

        # ASSERT
        self.assertEqual(action["res_model"], "mrp.production")
        self.assertEqual(
            action["res_id"],
            self.incoming_picking.flowable_production_ids[0].id,
        )

    def test_action_view_mrp_production_multiple(self):
        """
        Test that action_view_mrp_production returns a list view when there
        are multiple productions linked to the picking.

        PRE:    - A picking with multiple flowable productions
        ACT:    - Call action_view_mrp_production
        POST:   - Action opens a list filtered by production ids
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-MULTI-LOT")

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )
        self.incoming_picking.button_validate()

        # Create a second production manually linked to the same picking
        self.env["mrp.production"].create(
            {
                "product_id": self.product_flowable_1.id,
                "product_qty": 5,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "picking_type_id": self.picking_type_mrp_operation_1.id,
                "location_src_id": self.location_flowable_1.id,
                "location_dest_id": self.location_flowable_1.id,
                "picking_id": self.incoming_picking.id,
            }
        )

        # ACT
        action = self.incoming_picking.action_view_mrp_production()

        # ASSERT
        self.assertIn("domain", action)
        self.assertEqual(
            action["domain"],
            [("id", "in", self.incoming_picking.flowable_production_ids.ids)],
        )

    def test_mrp_operation_type_without_sequence_raises_error(self):
        """
        Test that a flowable mrp_operation picking type without a sequence
        raises an error during picking validation.

        PRE:    - A flowable mrp_operation picking type without sequence_id
        ACT:    - Validate a picking to a flowable location
        POST:   - UserError is raised about missing sequence
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.picking_type_mrp_operation_1.sequence_id = False

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-NOSEQ-LOT")

        self.env["stock.move.line"].create(
            {
                "picking_id": self.incoming_picking.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.incoming_picking.location_dest_id.id,
                "company_id": self.env.company.id,
            }
        )

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            self.incoming_picking.button_validate()

        msg_error = "Not found sequence in flowable manufacturing picking type %s"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_non_lot_tracked_product_at_flowable_location(self):
        """
        Test that receiving a product whose tracking was changed from 'lot'
        to 'none' after being added to the flowable allowed products raises
        an error during picking validation.

        PRE:    - A product added to flowable allowed products with tracking=lot
                - Product tracking changed to 'none' afterwards
        ACT:    - Validate an incoming picking with that product
        POST:   - UserError about product tracking
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        product_nolot = self.env["product.product"].create(
            {
                "name": "ProductNoLot",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_litre").id,
                "uom_po_id": self.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )
        self.location_flowable_1.write(
            {"flowable_allowed_product_ids": [(4, product_nolot.id)]}
        )
        # Change tracking after adding to allowed products (bypasses location constraint)
        product_nolot.tracking = "none"

        lot = self._create_lot(product_nolot, "TEST-NOLOT")
        picking = self._create_incoming_picking(
            self.location_flowable_1, product_nolot, lot, 10
        )

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            picking.button_validate()

        msg_error = "Product %s must be tracked by lot"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_auto_lot_creation_with_sequence(self):
        """
        Test that receiving stock at a flowable location with
        flowable_create_lots=True auto-creates a lot from the sequence.

        PRE:    - location_flowable_2 has flowable_create_lots=True and
                  flowable_sequence_id set
        ACT:    - Validate an incoming picking to location_flowable_2
        POST:   - The auto-created production has a lot_producing_id
                  different from the incoming lot
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_2.flowable_allowed_product_ids[0]

        lot = self._create_lot(product, "TEST-AUTOLOT")
        picking = self._create_incoming_picking(
            self.location_flowable_2, product, lot, 50
        )

        # ACT
        picking.button_validate()

        production = self._find_flowable_production(self.location_flowable_2)

        # ASSERT
        self.assertTrue(production.lot_producing_id)
        self.assertNotEqual(production.lot_producing_id, lot)

    def test_reception_blocks_flowable_location(self):
        """
        Test that validating a reception to a flowable location blocks it
        and creates a manufacturing order linked to the location.

        PRE:    - A flowable location with no active production
        ACT:    - Validate an incoming picking to that location
        POST:   - The location is blocked (flowable_blocked is True)
                - A manufacturing order is linked to the location
                - The MO is linked back to the picking
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.assertFalse(self.location_flowable_1.flowable_blocked)

        lot = self._create_lot(self.product_flowable_1, "TEST-BLOCK-LOT")
        picking = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot, 10
        )

        # ACT
        picking.button_validate()

        # ASSERT
        self.assertTrue(self.location_flowable_1.flowable_blocked)
        production = self.location_flowable_1.flowable_production_id
        self.assertTrue(production)
        self.assertEqual(production.picking_id, picking)

    def test_second_reception_to_blocked_location_rejected(self):
        """
        Test that a second reception to a blocked flowable location
        is rejected.

        PRE:    - A flowable location blocked by a first reception
                - A second incoming picking prepared before the location
                  was blocked
        ACT:    - Try to validate the second incoming picking
        POST:   - An error is raised about the location being blocked
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-BLOCK-LOT1")
        first_picking = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot_1, 10
        )

        lot_2 = self._create_lot(self.product_flowable_1, "TEST-BLOCK-LOT2")
        second_picking = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot_2, 10
        )

        first_picking.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)

        # ACT & ASSERT
        with self.assertRaises(Exception):
            second_picking.button_validate()

    def test_reception_after_mo_completed_succeeds(self):
        """
        Test the full cycle: reception blocks the location, completing
        the MO unblocks it, and a new reception succeeds.

        PRE:    - A flowable location with no active production
        ACT:    - Validate a first reception (location gets blocked)
                - Complete the resulting MO (location gets unblocked)
                - Validate a second reception
        POST:   - The location is unblocked after completing the MO
                - The second reception succeeds and creates a new MO
                - The location is blocked again by the new MO
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-CYCLE-LOT1")
        first_picking = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot_1, 10
        )

        # ACT 1 - First reception blocks the location
        first_picking.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)
        first_production = self.location_flowable_1.flowable_production_id

        # ACT 2 - Complete the MO, location gets unblocked
        first_production.button_mark_done()
        self.assertFalse(self.location_flowable_1.flowable_blocked)

        # ACT 3 - Second reception succeeds and blocks again
        lot_2 = self._create_lot(self.product_flowable_1, "TEST-CYCLE-LOT2")
        second_picking = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot_2, 5
        )
        second_picking.button_validate()

        # ASSERT
        self.assertTrue(self.location_flowable_1.flowable_blocked)
        second_production = self.location_flowable_1.flowable_production_id
        self.assertTrue(second_production)
        self.assertNotEqual(first_production, second_production)
        self.assertEqual(second_production.picking_id, second_picking)

    def test_blocking_is_per_location(self):
        """
        Test that blocking one flowable location does not affect another.

        PRE:    - Two flowable locations with no active production
        ACT:    - Validate a reception to location 1 (blocks it)
                - Validate a reception to location 2
        POST:   - Location 1 is blocked
                - Location 2 reception succeeds and blocks location 2
                  independently
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_1 = self._create_lot(self.product_flowable_1, "TEST-PERLOC-LOT1")
        picking_1 = self._create_incoming_picking(
            self.location_flowable_1, self.product_flowable_1, lot_1, 10
        )

        lot_2 = self._create_lot(self.product_flowable_1, "TEST-PERLOC-LOT2")
        picking_2 = self._create_incoming_picking(
            self.location_flowable_2, self.product_flowable_1, lot_2, 10
        )

        # ACT
        picking_1.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)
        self.assertFalse(self.location_flowable_2.flowable_blocked)

        picking_2.button_validate()

        # ASSERT
        self.assertTrue(self.location_flowable_1.flowable_blocked)
        self.assertTrue(self.location_flowable_2.flowable_blocked)
        self.assertNotEqual(
            self.location_flowable_1.flowable_production_id,
            self.location_flowable_2.flowable_production_id,
        )

    def test_auto_lot_location_also_gets_blocked(self):
        """
        Test that a flowable location with flowable_create_lots=True
        also gets blocked after a reception.

        PRE:    - location_flowable_2 has flowable_create_lots=True
        ACT:    - Validate a reception to location_flowable_2
        POST:   - The location is blocked
                - The MO uses an auto-generated lot (different from the
                  incoming lot)
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_2.flowable_allowed_product_ids[0]

        lot = self._create_lot(product, "TEST-AUTOLOT-BLOCK")
        picking = self._create_incoming_picking(
            self.location_flowable_2, product, lot, 50
        )

        # ACT
        picking.button_validate()

        # ASSERT
        self.assertTrue(self.location_flowable_2.flowable_blocked)
        production = self.location_flowable_2.flowable_production_id
        self.assertTrue(production)
        self.assertNotEqual(production.lot_producing_id, lot)

    def test_non_flowable_location_not_affected(self):
        """
        Test that receiving stock at a non-flowable location does not
        trigger any blocking or MO creation.

        PRE:    - A regular (non-flowable) internal location
        ACT:    - Validate an incoming picking to that location
        POST:   - No flowable_production_id is set
                - No MO is created for the picking
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        product = self.product_flowable_1
        lot = self._create_lot(product, "TEST-NONFLOW-LOT")
        picking = self._create_incoming_picking(self.location_1, product, lot, 10)

        # ACT
        picking.button_validate()

        # ASSERT
        self.assertFalse(self.location_1.flowable_storage)
        self.assertFalse(picking.flowable_production_ids)

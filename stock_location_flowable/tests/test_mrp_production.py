# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round

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

    def _create_flowable_picking_and_validate(self, location, product, lot, qty):
        """Helper to create and validate an incoming picking to a flowable location."""
        return self._receive_stock_at_location(location, product, lot, qty)

    def _receive_stock_at_location(
        self, location, product, lot, qty, picking_type=None
    ):
        """Helper to create and validate an incoming picking to any location."""
        if picking_type is None:
            picking_type = self.picking_type_incoming_1
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": location.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": qty,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": location.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()
        return picking

    def _find_flowable_production(self, location):
        """Helper to find the latest flowable MO for a location."""
        return self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", location.id),
            ],
            order="id desc",
            limit=1,
        )

    def _get_location_quants(self, location, product):
        """Helper to get all quants at a location for a product."""
        return self.env["stock.quant"].search(
            [
                ("location_id", "=", location.id),
                ("product_id", "=", product.id),
            ]
        )

    def _seed_flowable_location(self, location, product, lot, qty):
        """Receive initial stock at a flowable location and complete the resulting MO.

        This simulates how a user would put initial stock into a flowable
        location: receiving via an incoming picking, which triggers the
        creation of a mixing MO, and then completing that MO so the
        location is unblocked and ready for the actual test.
        """
        self._receive_stock_at_location(location, product, lot, qty)
        production = self._find_flowable_production(location)
        if production:
            production.button_mark_done()

    def test_flowable_mixing_produces_single_positive_quant(self):
        """
        Test that after completing a mixing MO, the flowable location has
        exactly one quant with positive quantity (the mixed lot).

        PRE:    - A flowable location with an initial lot quant (100 L)
        ACT:    - Receive 50 L at the flowable location (creates mixing MO)
                - Complete the mixing MO
        POST:   - Exactly one quant with positive quantity remains
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-INITIAL-LOT",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot_initial, 100
        )

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-NEW-LOT",
                "product_id": self.product_flowable_1.id,
            }
        )

        # ACT
        self._create_flowable_picking_and_validate(
            self.location_flowable_1, self.product_flowable_1, lot_new, 50
        )
        production = self._find_flowable_production(self.location_flowable_1)
        self.assertTrue(production, "Mixing MO should have been created")
        production.button_mark_done()

        # ASSERT
        remaining_quants = self._get_location_quants(
            self.location_flowable_1, self.product_flowable_1
        )
        positive_quants = remaining_quants.filtered(lambda q: q.quantity > 0)
        self.assertEqual(
            len(positive_quants),
            1,
            "Only one quant with positive quantity should remain (the mixed lot)",
        )

    def test_flowable_no_accumulated_error_after_multiple_mixing_cycles(self):
        """
        Test that multiple mixing cycles produce a clean single quant.

        PRE:    - A flowable location (capacity 1000 L)
        ACT:    - Perform 5 sequential mixing cycles with varying quantities
        POST:   - Only 1 quant with positive quantity exists
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        quantities = [50, 30, 45, 25, 20]

        for i, qty in enumerate(quantities):
            lot = self.env["stock.production.lot"].create(
                {
                    "name": f"TEST-MULTI-LOT-{i}",
                    "product_id": self.product_flowable_1.id,
                }
            )

            # ACT
            self._create_flowable_picking_and_validate(
                self.location_flowable_1, self.product_flowable_1, lot, qty
            )
            production = self._find_flowable_production(self.location_flowable_1)
            self.assertTrue(production, f"Mixing MO should be created on cycle {i + 1}")
            production.button_mark_done()

        # ASSERT
        remaining_quants = self._get_location_quants(
            self.location_flowable_1, self.product_flowable_1
        )
        positive_quants = remaining_quants.filtered(lambda q: q.quantity > 0)
        self.assertEqual(
            len(positive_quants),
            1,
            "Only one quant should remain after multiple mixing cycles",
        )

    def test_flowable_old_quants_go_to_exact_zero(self):
        """
        Test that when a mixing MO consumes old lot quants, they go to
        exactly 0.0 (IEEE 754 exact) — not a near-zero residual.

        This verifies that the raw move lines use the exact quant quantities
        (no float_round on individual consumption), so each quant is
        decremented by exactly its own value → result is 0.0.

        PRE:    - A flowable location with 1 lot at 100 L
        ACT:    - Receive 50 L (creates mixing MO, but don't complete it yet)
                - Check old quant after MO raw moves are processed
        POST:   - Old lot quant quantity is exactly 0.0 (or cleaned up)
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-EXACT-ZERO-OLD",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot_initial, 100
        )

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-EXACT-ZERO-NEW",
                "product_id": self.product_flowable_1.id,
            }
        )

        # ACT
        self._create_flowable_picking_and_validate(
            self.location_flowable_1, self.product_flowable_1, lot_new, 50
        )
        production = self._find_flowable_production(self.location_flowable_1)
        production.button_mark_done()

        # ASSERT: old lot quant should not exist or be exactly 0
        old_quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.location_flowable_1.id),
                ("product_id", "=", self.product_flowable_1.id),
                ("lot_id", "=", lot_initial.id),
            ]
        )
        if old_quant:
            self.assertEqual(
                old_quant.quantity,
                0.0,
                "Old lot quant should be exactly 0.0, not a near-zero residual",
            )

    def test_flowable_mixing_with_fractional_quantities(self):
        """
        Test that mixing works correctly with fractional quantities
        that could introduce floating point errors (e.g., from UoM conversions).

        PRE:    - A flowable location with a fractional lot quantity (33.333 L)
        ACT:    - Receive 16.667 L at the flowable location (creates mixing MO)
                - Complete the mixing MO
        POST:   - Only 1 quant with positive quantity exists
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-FRAC-INITIAL",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot_initial, 33.333
        )

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-FRAC-NEW",
                "product_id": self.product_flowable_1.id,
            }
        )

        # ACT
        self._create_flowable_picking_and_validate(
            self.location_flowable_1, self.product_flowable_1, lot_new, 16.667
        )
        production = self._find_flowable_production(self.location_flowable_1)
        production.button_mark_done()

        # ASSERT
        remaining_quants = self._get_location_quants(
            self.location_flowable_1, self.product_flowable_1
        )
        positive_quants = remaining_quants.filtered(lambda q: q.quantity > 0)
        self.assertEqual(len(positive_quants), 1)

    def test_flowable_mixing_does_not_affect_non_flowable_quants(self):
        """
        Test that completing a mixing MO at a flowable location does not
        affect quants at other (non-flowable) locations.

        PRE:    - A flowable location with stock
                - A non-flowable location with stock of the same product
        ACT:    - Complete a mixing MO at the flowable location
        POST:   - Non-flowable location quants are unaffected
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-NONFLO-INITIAL",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot_initial, 100
        )

        # Stock at non-flowable location
        lot_other = self.env["stock.production.lot"].create(
            {
                "name": "TEST-NONFLO-OTHER",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._receive_stock_at_location(
            self.location_1, self.product_flowable_1, lot_other, 200
        )

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-NONFLO-NEW",
                "product_id": self.product_flowable_1.id,
            }
        )

        # ACT
        self._create_flowable_picking_and_validate(
            self.location_flowable_1, self.product_flowable_1, lot_new, 50
        )
        production = self._find_flowable_production(self.location_flowable_1)
        production.button_mark_done()

        # ASSERT: non-flowable location quant is untouched
        other_quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.location_1.id),
                ("product_id", "=", self.product_flowable_1.id),
                ("lot_id", "=", lot_other.id),
            ]
        )
        self.assertEqual(
            other_quant.quantity,
            200,
            "Non-flowable location quant should not be affected by mixing MO",
        )

    def test_flowable_qty_producing_is_rounded(self):
        """
        Test that the mixing MO's qty_producing is properly rounded to the
        product's UoM rounding, so that _post_inventory produces a clean
        rounded finished quantity.

        PRE:    - A flowable location with stock
        ACT:    - Receive new stock (creates mixing MO)
        POST:   - MO's qty_producing == float_round(sum(quants), uom_rounding)
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        rounding = self.product_flowable_1.uom_id.rounding

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-ROUND-INITIAL",
                "product_id": self.product_flowable_1.id,
            }
        )
        self._seed_flowable_location(
            self.location_flowable_1, self.product_flowable_1, lot_initial, 100
        )

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-ROUND-NEW",
                "product_id": self.product_flowable_1.id,
            }
        )

        # ACT
        self._create_flowable_picking_and_validate(
            self.location_flowable_1, self.product_flowable_1, lot_new, 50
        )
        production = self._find_flowable_production(self.location_flowable_1)

        # ASSERT: qty_producing is properly rounded
        expected_qty = float_round(150.0, precision_rounding=rounding)
        self.assertEqual(
            production.qty_producing,
            expected_qty,
            f"qty_producing should be float_round({150.0}, rounding={rounding})"
            f" = {expected_qty}, got {production.qty_producing}",
        )

    def test_flowable_mixing_with_custom_uom_rounding(self):
        """
        Test the mixing process with a custom UoM that has fine rounding
        (0.001), simulating the customer's Litro(s) O2 configuration.

        Also tests with quantities that result from a Kg→Litro conversion
        (ratio 1.141) to exercise realistic float arithmetic.

        PRE:    - Custom UoM category with Litro O2 (rounding=0.001)
                - Product configured with this UoM
                - Flowable location configured with this UoM
                - Initial quant with a Kg-converted value
                - Decimal precision set to 5 (accommodates UoM rounding)
        ACT:    - Receive new stock with another Kg-converted quantity
                - Complete the mixing MO
        POST:   - Final stock is correct within UoM precision
        """
        # ARRANGE: Increase decimal precision to accommodate UoM rounding (0.001)
        dp = self.env.ref("product.decimal_product_uom")
        dp.digits = 5

        # Custom UoM with fine rounding (like customer's Litro O2)
        uom_category_o2 = self.env["uom.category"].create({"name": "Test Volumen O2"})
        uom_litro_o2 = self.env["uom.uom"].create(
            {
                "name": "Test Litro O2",
                "category_id": uom_category_o2.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )
        rounding = uom_litro_o2.rounding  # 0.001

        product_o2 = self.env["product.product"].create(
            {
                "name": "Test Oxigeno Liquido",
                "type": "product",
                "uom_id": uom_litro_o2.id,
                "uom_po_id": uom_litro_o2.id,
                "tracking": "lot",
            }
        )

        location_cistern = self.env["stock.location"].create(
            {
                "name": "Test Cisterna O2",
                "usage": "internal",
                "location_id": self.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
                "flowable_storage": True,
                "flowable_capacity": 5000,
                "flowable_uom_id": uom_litro_o2.id,
                "flowable_allowed_product_ids": [(4, product_o2.id)],
                "flowable_create_lots": True,
                "flowable_sequence_id": self.env.ref("stock.sequence_tracking").id,
            }
        )

        # Simulate quant from a Kg→Litro conversion: 657.93 Kg / 1.141
        # = 576.6257668712... L → rounded to 576.626
        kg_delivery_1 = 657.93
        litres_1 = float_round(
            kg_delivery_1 / 1.141, precision_rounding=rounding
        )  # 576.626

        lot_initial = self.env["stock.production.lot"].create(
            {
                "name": "TEST-O2-INITIAL",
                "product_id": product_o2.id,
            }
        )
        self.picking_type_mrp_operation_1.flowable_operation = True

        self._seed_flowable_location(
            location_cistern, product_o2, lot_initial, litres_1
        )

        # Second delivery: 583.21 Kg / 1.141 = 511.1393... → 511.139
        kg_delivery_2 = 583.21
        litres_2 = float_round(
            kg_delivery_2 / 1.141, precision_rounding=rounding
        )  # 511.139

        lot_new = self.env["stock.production.lot"].create(
            {
                "name": "TEST-O2-NEW",
                "product_id": product_o2.id,
            }
        )

        # ACT: Receive at the cistern
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": location_cistern.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product_o2.id,
                "product_uom_id": uom_litro_o2.id,
                "lot_id": lot_new.id,
                "qty_done": litres_2,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": location_cistern.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()

        # Find and complete the mixing MO
        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", location_cistern.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(production, "Mixing MO should have been created")
        production.button_mark_done()

        # ASSERT
        remaining = self.env["stock.quant"].search(
            [
                ("location_id", "=", location_cistern.id),
                ("product_id", "=", product_o2.id),
            ]
        )
        positive_quants = remaining.filtered(lambda q: q.quantity > 0)
        self.assertEqual(
            len(positive_quants),
            1,
            "Only one positive quant should remain (the mixed lot)",
        )
        expected_total = litres_1 + litres_2
        self.assertEqual(
            float_compare(
                positive_quants.quantity,
                expected_total,
                precision_rounding=rounding,
            ),
            0,
            f"Final stock {positive_quants.quantity} should equal total"
            f" {expected_total} within UoM rounding {rounding}",
        )

    def test_flowable_mixing_multiple_cycles_fine_rounding(self):
        """
        Test multiple mixing cycles with fine UoM rounding (0.001) and
        Kg→Litro converted quantities, verifying no error accumulation.

        Simulates 5 sequential deliveries converted from Kg O2 to Litro O2
        (ratio 1.141), ensuring the flowable location stays clean.

        PRE:    - Custom UoM with rounding=0.001
                - Decimal precision set to 5 (accommodates UoM rounding)
        ACT:    - 5 sequential receive → mix → complete cycles
        POST:   - Only 1 quant with positive quantity remains
                - Final stock within UoM precision of sum of deliveries
        """
        # ARRANGE: Increase decimal precision to accommodate UoM rounding (0.001)
        dp = self.env.ref("product.decimal_product_uom")
        dp.digits = 5

        self.picking_type_mrp_operation_1.flowable_operation = True

        uom_category_o2 = self.env["uom.category"].create(
            {"name": "Test Volumen O2 Multi"}
        )
        uom_litro_o2 = self.env["uom.uom"].create(
            {
                "name": "Test Litro O2 Multi",
                "category_id": uom_category_o2.id,
                "uom_type": "reference",
                "rounding": 0.001,
            }
        )
        rounding = uom_litro_o2.rounding

        product_o2 = self.env["product.product"].create(
            {
                "name": "Test Oxigeno Multi",
                "type": "product",
                "uom_id": uom_litro_o2.id,
                "uom_po_id": uom_litro_o2.id,
                "tracking": "lot",
            }
        )

        location_cistern = self.env["stock.location"].create(
            {
                "name": "Test Cisterna O2 Multi",
                "usage": "internal",
                "location_id": self.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
                "flowable_storage": True,
                "flowable_capacity": 10000,
                "flowable_uom_id": uom_litro_o2.id,
                "flowable_allowed_product_ids": [(4, product_o2.id)],
                "flowable_create_lots": True,
                "flowable_sequence_id": self.env.ref("stock.sequence_tracking").id,
            }
        )

        # Simulate 5 deliveries in Kg, converted to Litres
        kg_deliveries = [657.93, 583.21, 492.84, 701.23, 515.67]

        for i, kg in enumerate(kg_deliveries):
            litres = float_round(kg / 1.141, precision_rounding=rounding)

            lot = self.env["stock.production.lot"].create(
                {
                    "name": f"TEST-O2-MULTI-{i}",
                    "product_id": product_o2.id,
                }
            )

            picking = self.env["stock.picking"].create(
                {
                    "picking_type_id": self.picking_type_incoming_1.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": location_cistern.id,
                }
            )
            self.env["stock.move.line"].create(
                {
                    "picking_id": picking.id,
                    "product_id": product_o2.id,
                    "product_uom_id": uom_litro_o2.id,
                    "lot_id": lot.id,
                    "qty_done": litres,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": location_cistern.id,
                    "company_id": self.env.company.id,
                }
            )
            picking.button_validate()

            production = self.env["mrp.production"].search(
                [
                    (
                        "picking_type_id",
                        "=",
                        self.picking_type_mrp_operation_1.id,
                    ),
                    ("location_dest_id", "=", location_cistern.id),
                ],
                order="id desc",
                limit=1,
            )
            self.assertTrue(
                production, f"Mixing MO should be created on delivery {i + 1}"
            )
            production.button_mark_done()

        # ASSERT
        remaining = self.env["stock.quant"].search(
            [
                ("location_id", "=", location_cistern.id),
                ("product_id", "=", product_o2.id),
            ]
        )
        positive_quants = remaining.filtered(lambda q: q.quantity > 0)
        self.assertEqual(
            len(positive_quants),
            1,
            "Only one positive quant should remain after 5 cycles",
        )
        expected_total = sum(
            float_round(kg / 1.141, precision_rounding=rounding) for kg in kg_deliveries
        )
        self.assertEqual(
            float_compare(
                positive_quants.quantity,
                expected_total,
                precision_rounding=rounding,
            ),
            0,
            f"Final stock {positive_quants.quantity} should equal total"
            f" {expected_total} within UoM rounding {rounding}",
        )

    def test_production_flowable_computed(self):
        """
        Test that production_flowable is True when the picking type is flowable.

        PRE:    - A flowable MO created from a picking
        ACT:    - Read production_flowable
        POST:   - production_flowable is True
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self._find_flowable_production(self.location_flowable_1)

        # ACT & ASSERT
        self.assertTrue(production.production_flowable)

    def test_production_flowable_false_for_non_flowable_type(self):
        """
        Test that production_flowable is False when picking type is not flowable.

        PRE:    - A standard MO (non-flowable picking type)
        ACT:    - Read production_flowable
        POST:   - production_flowable is False
        """
        # ARRANGE
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product_flowable_1.id,
                "product_qty": 10,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "picking_type_id": self.picking_type_mrp_operation_1.id,
                "location_src_id": self.location_flowable_1.id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )

        # ACT & ASSERT
        self.assertFalse(production.production_flowable)

    def test_production_blocked_computed(self):
        """
        Test that production_blocked is True when a location references the MO.

        PRE:    - A flowable location with a production linked
        ACT:    - Read production_blocked
        POST:   - production_blocked is True
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self._find_flowable_production(self.location_flowable_1)

        # ACT & ASSERT
        self.assertTrue(production.production_blocked)

    def test_cancel_production_with_picking_raises_error(self):
        """
        Test that cancelling a production with a picking associated raises
        an error.

        PRE:    - A flowable MO with a picking_id set
        ACT:    - Try to cancel the MO
        POST:   - An error is raised because the picking is associated
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self._find_flowable_production(self.location_flowable_1)
        self.assertTrue(production.picking_id)

        # ACT & ASSERT
        # The cancel flow triggers stock_move.write which also blocks
        # modification, so we expect either UserError or ValidationError
        with self.assertRaises(Exception) as error:
            production.action_cancel()

        # Verify the error is related to the mixing being in progress
        self.assertIn("mixing is in progress", str(error.exception))

    def test_write_to_close_production_with_picking_raises_error(self):
        """
        Test that modifying a to_close production with a picking raises
        a ValidationError.

        PRE:    - A flowable MO in to_close state with a picking_id
        ACT:    - Try to write to the MO
        POST:   - ValidationError is raised
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self._find_flowable_production(self.location_flowable_1)
        self.assertTrue(production.picking_id)
        self.assertEqual(production.state, "to_close")

        # ACT & ASSERT
        with self.assertRaises(ValidationError) as error:
            production.write({"product_qty": 999})

        msg_error = (
            "You cannot modify a mix production with a picking associated."
            " The mixing is in progress."
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_production_without_bom_allowed_for_flowable(self):
        """
        Test that a flowable production can be created without a Bill of
        Materials because _check_production_lines is bypassed.

        PRE:    - A flowable mrp_operation picking type
        ACT:    - Create a production without BoM
        POST:   - Production is created successfully
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        # ACT
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product_flowable_1.id,
                "product_qty": 10,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "picking_type_id": self.picking_type_mrp_operation_1.id,
                "location_src_id": self.location_flowable_1.id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )

        # ASSERT
        self.assertTrue(production)

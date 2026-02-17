# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import UserError, ValidationError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockLocation(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockLocation, cls).setUpClass()
        cls.uom_litre = cls.env.ref("uom.product_uom_litre")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_flowable_1 = cls.env["product.product"].create(
            {
                "name": "Test CO2 1",
                "type": "product",
                "uom_id": cls.uom_litre.id,
                "uom_po_id": cls.uom_litre.id,
            }
        )
        cls.warehouse_bcn = cls.env["stock.warehouse"].create(
            {
                "name": "Test Barcelona",
                "code": "BCN",
            }
        )
        cls.location_flowable_bcn_1 = cls.env["stock.location"].create(
            {
                "name": "Test Flowable bcn 1",
                "location_id": cls.warehouse_bcn.lot_stock_id.id,
            }
        )

    # check
    def test_required_field_flowable_capacity(self):
        """
        Test to ensure that 'flowable_capacity' field is required when
        'flowable_storage' is True.

        PRE:    - location_flowable_bcn_1 exists
                - 'flowable_storage' is set to True
        ACT:    - Attempt to write to location_flowable_bcn_1 with 'flowable_storage'
         but without 'flowable_capacity'
        POST:   - ValidationError is raised
        """
        # ARRANGE & ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_storage": True,
                }
            )

        # ASSERT
        msg_error = "Capacity must be greater than 0"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_required_field_flowable_uom_id(self):
        """
        Test to ensure that 'flowable_uom_id' field is required when 'flowable_storage'
         is True.

        PRE:    - location_flowable_bcn_1 exists
                - 'flowable_storage' is set to True
                - 'flowable_capacity' is set
        ACT:    - Attempt to write to location_flowable_bcn_1 with 'flowable_storage'
         and 'flowable_capacity' but without 'flowable_uom_id'
        POST:   - ValidationError is raised
        """
        # ARRANGE & ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_storage": True,
                    "flowable_capacity": 100.0,
                }
            )

        # ASSERT
        msg_error = "You must select a unit of measure"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_required_field_flowable_allowed_product_ids(self):
        """
        Test to ensure that 'flowable_allowed_product_ids' field is required when
        'flowable_storage' is True.

        PRE:    - location_flowable_bcn_1 exists
                - 'flowable_storage' is set to True
                - 'flowable_capacity' is set
                - 'flowable_uom_id' is set
        ACT:    - Attempt to write to location_flowable_bcn_1 with 'flowable_storage',
                'flowable_capacity' and
                'flowable_uom_id' but without 'flowable_allowed_product_ids'
        POST:   - ValidationError is raised
        """
        # ARRANGE & ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_storage": True,
                    "flowable_capacity": 100.0,
                    "flowable_uom_id": self.uom_litre.id,
                }
            )

        # ASSERT
        msg_error = "You must select products"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_flowable_allowed_product_ids_tracked_by_lot(self):
        """
        Test to ensure that 'flowable_allowed_product_ids' field has products tracked
        by lot.

        PRE:    - location_flowable_bcn_1 exists
                - 'flowable_storage' is set to True
                - 'flowable_capacity' is set
                - 'flowable_uom_id' is set
                - 'flowable_allowed_product_ids' is set
        ACT:    - Attempt to write to location_flowable_bcn_1 with 'flowable_storage',
                'flowable_capacity',
                'flowable_uom_id' and 'flowable_allowed_product_ids' but without
                products tracked by lot
        POST:   - ValidationError is raised
        """
        # ARRANGE & ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_storage": True,
                    "flowable_capacity": 100.0,
                    "flowable_uom_id": self.uom_litre.id,
                    "flowable_allowed_product_ids": [(4, self.product_flowable_1.id)],
                }
            )

        # ASSERT
        msg_error = "All allowed products must be tracked by lot"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_successful_flowable_location_update(self):
        """
        Test to ensure that a location can be successfully updated with all required
        fields.

        PRE:  - location_flowable_bcn_1 exists
              - Necessary fields are prepared (uom_litre, product_flowable_1)
        ACT:  - Write to location_flowable_bcn_1 with all required fields
        POST: - No errors are raised
              - All fields are correctly updated
        """
        # ARRANGE
        self.product_flowable_1.tracking = "lot"

        self.location_flowable_bcn_1.write(
            {
                "flowable_storage": True,
                "flowable_capacity": 100.0,
                "flowable_uom_id": self.uom_litre.id,
                "flowable_allowed_product_ids": [(4, self.product_flowable_1.id)],
            }
        )

        # ACT & ASSERT
        self.assertTrue(self.location_flowable_bcn_1.flowable_storage)
        self.assertEqual(self.location_flowable_bcn_1.flowable_capacity, 100.0)
        self.assertEqual(
            self.location_flowable_bcn_1.flowable_uom_id.id, self.uom_litre.id
        )
        self.assertIn(
            self.product_flowable_1.id,
            self.location_flowable_bcn_1.flowable_allowed_product_ids.ids,
        )

    # check
    def test_adding_product_with_incompatible_uom(self):
        """
        Test to ensure that adding a product with a unit of measure different from
        'flowable_uom_id'
        raises an error.

        PRE:    - Location exists with 'flowable_storage' set to True and a certain
                'flowable_uom_id'
                - A product with a different 'uom_id' exists
        ACT:    - Attempt to add this product to 'flowable_allowed_product_ids'
        POST:   - ValidationError is raised stating that only products with the allowed
                unit of measure can be assigned
        """
        # ARRANGE
        product_flowable_2 = self.env["product.product"].create(
            {
                "name": "Test CO2 2",
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "tracking": "lot",
            }
        )

        # ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_storage": True,
                    "flowable_capacity": 100.0,
                    "flowable_uom_id": self.uom_litre.id,
                    "flowable_allowed_product_ids": [(4, product_flowable_2.id)],
                }
            )

        # ASSERT
        msg_error = (
            "The product %s is measured in %s. You can only assign"
            " products that have the allowed unit of measure"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_changing_to_incompatible_uom_id(self):
        """
        Test to ensure that changing 'flowable_uom_id' to a unit of measure different
        from that of
        allowed products raises an error.

        PRE:    - Location exists with 'flowable_storage' set to True and a certain
                'flowable_uom_id'
                - 'flowable_allowed_product_ids' contains products with the current
                'flowable_uom_id'
        ACT:    - Attempt to change 'flowable_uom_id' to a different unit of measure
        POST:   - ValidationError is raised stating that only products with the allowed unit
                of measure can be assigned
        """
        # ARRANGE
        product_flowable_2 = self.env["product.product"].create(
            {
                "name": "Test CO2 2",
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "tracking": "lot",
            }
        )

        self.location_flowable_bcn_1.write(
            {
                "flowable_storage": True,
                "flowable_capacity": 100.0,
                "flowable_uom_id": self.uom_unit.id,
                "flowable_allowed_product_ids": [(4, product_flowable_2.id)],
            }
        )

        # ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_uom_id": self.uom_litre.id,
                }
            )

        # ASSERT
        msg_error = (
            "The product %s is measured in %s. You can only assign"
            " products that have the allowed unit of measure"
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    # check
    def test_check_flowable_sequence_id(self):
        # ARRANGE
        self.product_flowable_1.tracking = "lot"

        self.location_flowable_bcn_1.write(
            {
                "flowable_storage": True,
                "flowable_capacity": 100.0,
                "flowable_uom_id": self.uom_litre.id,
                "flowable_allowed_product_ids": [(4, self.product_flowable_1.id)],
            }
        )

        # ACT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_bcn_1.write(
                {
                    "flowable_create_lots": True,
                }
            )

        # ASSERT
        msg_error = "You must select a sequence"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_disable_flowable_storage_clears_fields(self):
        """
        Test that disabling flowable_storage on a location clears all
        flowable-related fields.

        PRE:    - A fully configured flowable location
        ACT:    - Set flowable_storage to False
        POST:   - All flowable fields are cleared
        """
        # ARRANGE
        self.product_flowable_1.tracking = "lot"
        self.location_flowable_bcn_1.write(
            {
                "flowable_storage": True,
                "flowable_capacity": 100.0,
                "flowable_uom_id": self.uom_litre.id,
                "flowable_allowed_product_ids": [(4, self.product_flowable_1.id)],
            }
        )

        # ACT
        self.location_flowable_bcn_1.write({"flowable_storage": False})

        # ASSERT
        self.assertFalse(self.location_flowable_bcn_1.flowable_storage)
        self.assertEqual(self.location_flowable_bcn_1.flowable_capacity, 0)
        self.assertFalse(self.location_flowable_bcn_1.flowable_uom_id)
        self.assertFalse(self.location_flowable_bcn_1.flowable_sequence_id)

    def test_cannot_disable_flowable_on_blocked_location(self):
        """
        Test that disabling flowable_storage on a blocked location
        (one with a production linked) raises an error.

        PRE:    - A flowable location with a production linked
        ACT:    - Attempt to set flowable_storage to False
        POST:   - ValidationError is raised
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()
        self.assertTrue(self.location_flowable_1.flowable_blocked)

        # ACT & ASSERT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_1.write({"flowable_storage": False})

        msg_error = "You cannot disable flowable storage from a blocked location."
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_flowable_blocked_popover(self):
        """
        Test that the flowable_blocked_popover computed field returns
        a JSON string with the expected warning message.

        PRE:    - A flowable location
        ACT:    - Read flowable_blocked_popover
        POST:   - Contains expected title and message
        """
        # ACT & ASSERT
        popover = self.location_flowable_1.flowable_blocked_popover
        self.assertIn("Flowable Location Warning", popover)
        self.assertIn("manufacturing order", popover)

    def test_flowable_capacity_occupied(self):
        """
        Test that flowable_capacity_occupied computes the sum of quant quantities.

        PRE:    - A flowable location with stock
        ACT:    - Receive stock and check capacity_occupied
        POST:   - capacity_occupied reflects the stock
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {
                "name": "TEST-CAP-LOT",
                "product_id": product.id,
            }
        )

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": 100,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()

        # ACT
        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", self.location_flowable_1.id),
            ],
            order="id desc",
            limit=1,
        )
        production.button_mark_done()

        # ASSERT
        self.location_flowable_1.invalidate_cache()
        self.assertGreater(self.location_flowable_1.flowable_capacity_occupied, 0)

    def test_flowable_percentage_occupied(self):
        """
        Test that flowable_percentage_occupied is calculated correctly.

        PRE:    - A flowable location with capacity=1000 and no stock
        ACT:    - Read percentage_occupied
        POST:   - percentage is 0 when empty
        """
        # ACT & ASSERT
        self.assertEqual(self.location_flowable_1.flowable_percentage_occupied, 0)

    def test_flowable_percentage_zero_capacity(self):
        """
        Test that flowable_percentage_occupied returns 0 when capacity is 0.

        PRE:    - A non-flowable location with capacity=0
        ACT:    - Read flowable_percentage_occupied
        POST:   - Returns 0 (no division by zero)
        """
        # ACT & ASSERT
        self.assertEqual(self.location_flowable_bcn_1.flowable_percentage_occupied, 0)

    def test_action_view_mrp_production(self):
        """
        Test that the action_view_mrp_production method returns an action
        pointing to the linked production.

        PRE:    - A flowable location with a production linked
        ACT:    - Call action_view_mrp_production
        POST:   - Action res_id matches the production
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        production = self.location_flowable_1.flowable_production_id

        # ACT
        action = self.location_flowable_1.action_view_mrp_production()

        # ASSERT
        self.assertEqual(action["res_id"], production.id)
        self.assertEqual(action["res_model"], "mrp.production")

    def test_complete_name_blocked(self):
        """
        Test that the complete_name of a blocked flowable location
        includes '[Blocked]'.

        PRE:    - A flowable location that is blocked
        ACT:    - Read complete_name
        POST:   - Contains 'Blocked'
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        # ACT & ASSERT
        self.assertIn("Blocked", self.location_flowable_1.complete_name)

    def test_name_get_blocked(self):
        """
        Test that name_get for a blocked flowable location includes '[Blocked]'.

        PRE:    - A flowable location that is blocked
        ACT:    - Call name_get
        POST:   - Display name contains '[Blocked]'
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        self.incoming_picking.button_validate()

        # ACT
        result = self.location_flowable_1.name_get()

        # ASSERT
        self.assertIn("[Blocked]", result[0][1])

    def test_name_get_not_blocked(self):
        """
        Test that name_get for a non-blocked flowable location does NOT
        include '[Blocked]'.

        PRE:    - A flowable location that is not blocked
        ACT:    - Call name_get
        POST:   - Display name does not contain '[Blocked]'
        """
        # ACT
        result = self.location_flowable_1.name_get()

        # ASSERT
        self.assertNotIn("[Blocked]", result[0][1])

    def test_cannot_remove_stored_product_from_allowed(self):
        """
        Test that removing a product from flowable_allowed_product_ids
        raises an error when stock of that product exists.

        PRE:    - A flowable location with stock of a product
        ACT:    - Try to remove that product from allowed list
        POST:   - UserError is raised
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {
                "name": "TEST-REMOVE-LOT",
                "product_id": product.id,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": 50,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()

        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", self.location_flowable_1.id),
            ],
            order="id desc",
            limit=1,
        )
        production.button_mark_done()

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            self.location_flowable_1.write(
                {
                    "flowable_allowed_product_ids": [
                        (3, product.id),
                    ],
                }
            )

        msg_error = (
            "You cannot remove a product that is currently" " stored in this location."
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_capacity_full_raises_error(self):
        """
        Test that receiving stock that fills the flowable location to its
        capacity triggers the capacity constraint.

        PRE:    - A flowable location with capacity 100
        ACT:    - Receive 100 litres (exactly the capacity)
        POST:   - ValidationError is raised about location capacity being full
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True

        self.location_flowable_1.write({"flowable_capacity": 100})
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {"name": "TEST-FULL-LOT", "product_id": product.id}
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": 100,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )

        # ACT & ASSERT
        with self.assertRaises(ValidationError) as error:
            picking.button_validate()

        msg_error = "Location capacity is full"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_reduce_capacity_below_occupied(self):
        """
        Test that reducing a flowable location's capacity below the occupied
        amount is blocked.

        PRE:    - A flowable location with stock (capacity_occupied > 0)
        ACT:    - Try to reduce capacity below the occupied amount
        POST:   - ValidationError is raised because occupied >= new capacity
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {"name": "TEST-REDUCECAP-LOT", "product_id": product.id}
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": 100,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()

        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", self.location_flowable_1.id),
            ],
            order="id desc",
            limit=1,
        )
        production.button_mark_done()

        # ACT & ASSERT
        with self.assertRaises(ValidationError):
            self.location_flowable_1.write({"flowable_capacity": 50})

    def test_change_uom_with_existing_stock(self):
        """
        Test that changing flowable_uom_id when quants with a different UoM
        exist at the location is blocked.

        PRE:    - A flowable location with stock (quants in litres)
        ACT:    - Change flowable_uom_id to a different UoM
        POST:   - ValidationError about different unit of measure
        """
        # ARRANGE
        self.picking_type_mrp_operation_1.flowable_operation = True
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {"name": "TEST-UOM-LOT", "product_id": product.id}
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_incoming_1.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "lot_id": lot.id,
                "qty_done": 50,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location_flowable_1.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()

        production = self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", self.picking_type_mrp_operation_1.id),
                ("location_dest_id", "=", self.location_flowable_1.id),
            ],
            order="id desc",
            limit=1,
        )
        production.button_mark_done()

        # Create a new product with units UoM to make the change valid
        # for the allowed products constraint, isolating _check_flowable_uom_id
        product_unit = self.env["product.product"].create(
            {
                "name": "Test Product Units",
                "type": "product",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "tracking": "lot",
            }
        )

        # ACT & ASSERT
        with self.assertRaises(ValidationError) as error:
            self.location_flowable_1.write(
                {
                    "flowable_uom_id": self.uom_unit.id,
                    "flowable_allowed_product_ids": [
                        (6, 0, [product_unit.id]),
                    ],
                }
            )

        msg_error = "You have stock movements with different unit of measure"
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_convert_location_with_unmixed_products(self):
        """
        Test that enabling flowable_storage on a location that already has
        multiple positive quants of the same product is blocked.

        PRE:    - A non-flowable location with two lots of the same product
        ACT:    - Try to enable flowable_storage
        POST:   - UserError about unmixed products
        """
        # ARRANGE — add two lots via inventory adjustments
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot_1 = self.env["stock.production.lot"].create(
            {"name": "UNMIXED-LOT-1", "product_id": product.id}
        )
        lot_2 = self.env["stock.production.lot"].create(
            {"name": "UNMIXED-LOT-2", "product_id": product.id}
        )

        inventory = self.env["stock.inventory"].create({"name": "Add unmixed stock"})
        inventory.action_start()
        self.env["stock.inventory.line"].create(
            [
                {
                    "inventory_id": inventory.id,
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "location_id": self.location_1.id,
                    "prod_lot_id": lot_1.id,
                    "product_qty": 50,
                },
                {
                    "inventory_id": inventory.id,
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "location_id": self.location_1.id,
                    "prod_lot_id": lot_2.id,
                    "product_qty": 30,
                },
            ]
        )
        inventory.action_validate()

        # ACT & ASSERT
        with self.assertRaises(UserError) as error:
            self.location_1.write(
                {
                    "flowable_storage": True,
                    "flowable_capacity": 1000,
                    "flowable_uom_id": product.uom_id.id,
                    "flowable_allowed_product_ids": [(4, product.id)],
                }
            )

        msg_error = (
            "You cannot convert this location into a flowable location"
            " because there are unmixed products."
        )
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

    def test_capacity_occupied_zero_for_non_flowable_location(self):
        """
        Test that a non-flowable location always has
        flowable_capacity_occupied = 0 even if it has stock.

        PRE:    - A non-flowable location with stock
        ACT:    - Read flowable_capacity_occupied
        POST:   - Value is 0
        """
        # ARRANGE — add stock via inventory adjustment
        product = self.location_flowable_1.flowable_allowed_product_ids[0]

        lot = self.env["stock.production.lot"].create(
            {"name": "NONFLO-LOT", "product_id": product.id}
        )
        inventory = self.env["stock.inventory"].create(
            {"name": "Add stock to non-flowable"}
        )
        inventory.action_start()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": self.location_1.id,
                "prod_lot_id": lot.id,
                "product_qty": 200,
            }
        )
        inventory.action_validate()

        # ACT & ASSERT
        self.location_1.invalidate_cache()
        self.assertEqual(self.location_1.flowable_capacity_occupied, 0)

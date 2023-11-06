# Copyright NuoBiT Solutions - Frank Cespedes <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import ValidationError

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

    # Proposals for possible future tests to implement
    #
    # def test_flowable_capacity_constraints(self):
    #     with self.assertRaises(ValidationError):
    #         self.location.flowable_capacity = 50
    #     self.location.flowable_capacity = 150
    #     self.assertEqual(self.location.flowable_capacity, 150, "La capacity debe
    #     actualizarse good")
    #
    # def test_product_uom_constraints(self):
    #     self.location.write({
    #         'flowable_allowed_product_ids': [(4, self.product_flowable_1.id)],
    #         'flowable_uom_id': self.env.ref('uom.product_uom_dozen').id
    #     })
    #     with self.assertRaises(ValidationError):
    #         self.location._check_flowable_uom_id()
    #
    # def test_write_method(self):
    #     with self.assertRaises(ValidationError):
    #         self.location.write({'flowable_storage': False})
    #     self.location.flowable_production_id = False
    #     self.location.write({'flowable_storage': False})
    #     self.assertFalse(self.location.flowable_storage, "El flowable storage = False")
    #
    # def test_action_view_mrp_production(self):
    #     production = self.env['mrp.production'].create({})
    #     self.location.flowable_production_id = production
    #     action = self.location.action_view_mrp_production()
    #     self.assertEqual(action['res_id'], production.id, "La acción debería mostrar
    #     la orden de producción correcta")

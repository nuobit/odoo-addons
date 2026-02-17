# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.exceptions import ValidationError

from .test_common import TestCommon

_logger = logging.getLogger(__name__)


class TestStockQuant(TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockQuant, cls).setUpClass()

    def test_unique_lot_constraint_at_flowable_location(self):
        """
        Test that having more than one positive lot quant at a flowable location
        raises a ValidationError.

        A user who does two successive inventory adjustments at the same
        flowable location with different lots should be blocked on the second.

        PRE:    - A flowable location with stock from a first lot (via inventory)
        ACT:    - Perform a second inventory adjustment adding a different lot
        POST:   - ValidationError is raised about duplicate lots
        """
        # ARRANGE — first lot via inventory adjustment
        lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "QUANT-LOT-1",
                "product_id": self.product_flowable_1.id,
            }
        )

        inventory_1 = self.env["stock.inventory"].create(
            {
                "name": "Add first lot",
            }
        )
        inventory_1.action_start()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory_1.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "location_id": self.location_flowable_1.id,
                "prod_lot_id": lot_1.id,
                "product_qty": 100,
            }
        )
        inventory_1.action_validate()

        # ACT — second lot via inventory adjustment
        lot_2 = self.env["stock.production.lot"].create(
            {
                "name": "QUANT-LOT-2",
                "product_id": self.product_flowable_1.id,
            }
        )

        inventory_2 = self.env["stock.inventory"].create(
            {
                "name": "Add second lot",
            }
        )
        inventory_2.action_start()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory_2.id,
                "product_id": self.product_flowable_1.id,
                "product_uom_id": self.product_flowable_1.uom_id.id,
                "location_id": self.location_flowable_1.id,
                "prod_lot_id": lot_2.id,
                "product_qty": 50,
            }
        )

        # ASSERT
        with self.assertRaises(ValidationError) as error:
            inventory_2.action_validate()

        msg_error = "You cannot have more than one lot in the same location."
        msg_error = self.get_error_message_regex(msg_error)
        self.assertRegex(error.exception.args[0], msg_error)

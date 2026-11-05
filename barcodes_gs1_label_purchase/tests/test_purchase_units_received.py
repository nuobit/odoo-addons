# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from types import SimpleNamespace

from lxml import etree
from psycopg2 import IntegrityError

from odoo.tests import Form
from odoo.tools import mute_logger
from odoo.tools.safe_eval import safe_eval

from .common import TestPurchaseCommon


class TestPurchaseUnitsReceived(TestPurchaseCommon):
    def _purchase_palots(self, quantity):
        # palots of garlic, each weighed on receipt; 25 kg is only an estimate
        uom_palot = self._create_dynamic_uom("Palot", 25)
        product = self._create_product(
            "Garlic", "2000000000015", uom_id=self.uom_kg.id, uom_po_id=uom_palot.id
        )
        return self._purchase(product, quantity, uom_palot)

    def _validate_with_backorder(self, receipt, quantity, units):
        receipt.move_ids.write({"quantity": quantity, "purchase_uom_qty": units})
        receipt.with_context(skip_backorder=True).button_validate()
        return receipt.backorder_ids

    def _moves_list_shows_the_column(self, picking):
        # a list has no Form helper: evaluate the column's column_invisible on
        # the picking, as the web client does
        arch = picking.get_views([(False, "form")])["views"]["form"]["arch"]
        (column,) = etree.fromstring(arch).xpath(
            "//field[@name='move_ids_without_package']/list"
            "/field[@name='purchase_uom_qty']"
        )
        parent = SimpleNamespace(picking_type_code=picking.picking_type_code)
        return not safe_eval(column.get("column_invisible"), {"parent": parent})

    def test_receipt_proposes_the_units_bought(self):
        receipt = self._purchase_palots(4)
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 4)

    def test_receipt_proposes_a_part_of_a_unit_as_one(self):
        receipt = self._purchase_palots(2.5)
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 3)

    def test_backorder_proposes_the_units_still_to_come(self):
        receipt = self._purchase_palots(4)
        backorder = self._validate_with_backorder(receipt, 78, 3)
        self.assertEqual(backorder.move_ids.purchase_uom_qty, 1)

    def test_done_receipt_keeps_the_units_it_received(self):
        receipt = self._purchase_palots(4)
        self._validate_with_backorder(receipt, 78, 3)
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 3)

    def test_receipt_done_unread_keeps_the_units_it_proposes(self):
        receipt = self._purchase_palots(4)
        # validated without its proposal being read, as an automated flow does
        receipt.button_validate()
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 4)

    def test_backorder_proposes_no_units_once_more_than_bought_have_come(self):
        receipt = self._purchase_palots(4)
        # the vendor sent a palot more, lighter ones, and the rest was kept open
        backorder = self._validate_with_backorder(receipt, 92, 5)
        self.assertEqual(backorder.move_ids.purchase_uom_qty, 0)

    def test_split_receipt_proposes_what_its_first_part_did_not_bring(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.write({"quantity": 52, "purchase_uom_qty": 2})
        receipt.action_split_transfer()
        second_part = receipt.backorder_ids
        # while the first part is open, nothing has come yet
        self.assertEqual(second_part.move_ids.purchase_uom_qty, 4)
        receipt.button_validate()
        self.assertEqual(second_part.move_ids.purchase_uom_qty, 2)

    def test_split_receipt_keeps_the_units_entered_on_its_first_part(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.write({"quantity": 52, "purchase_uom_qty": 2})
        receipt.action_split_transfer()
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 2)

    def test_receipt_keeps_the_units_entered_when_the_order_changes(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.purchase_uom_qty = 3
        receipt.move_ids.purchase_line_id.product_qty = 6
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 3)

    def test_receipt_keeps_the_units_entered_when_it_is_weighed(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.purchase_uom_qty = 3
        receipt.move_ids.quantity = 78
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 3)

    def test_receipt_proposes_again_once_its_units_are_no_longer_entered(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.purchase_uom_qty = 3
        receipt.move_ids.purchase_uom_qty_entered = False
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 4)

    def test_receipt_proposal_follows_the_units_bought(self):
        receipt = self._purchase_palots(4)
        receipt.move_ids.purchase_line_id.product_qty = 6
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 6)

    def test_receipt_proposal_follows_units_bought_it_already_expects(self):
        receipt = self._purchase_palots(4)
        # the receipt already expects 6 palots, so the order adds no move to it
        receipt.move_ids.product_uom_qty = 150
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 4)
        receipt.move_ids.purchase_line_id.product_qty = 6
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 6)

    def test_receipt_proposes_units_once_its_unit_turns_dynamic(self):
        uom_palot = self._create_dynamic_uom("Palot", 25)
        # bought before the unit is marked dynamic
        uom_palot.dynamic_ratio = False
        product = self._create_product(
            "Garlic", "2000000000015", uom_id=self.uom_kg.id, uom_po_id=uom_palot.id
        )
        receipt = self._purchase(product, 4, uom_palot)
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 0)
        uom_palot.dynamic_ratio = True
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 4)

    def test_correction_on_a_done_receipt_moves_the_backorder_proposal(self):
        receipt = self._purchase_palots(4)
        backorder = self._validate_with_backorder(receipt, 78, 2)
        self.assertEqual(backorder.move_ids.purchase_uom_qty, 2)
        receipt.move_ids.purchase_uom_qty = 3
        self.assertEqual(backorder.move_ids.purchase_uom_qty, 1)

    def test_return_has_no_units_received(self):
        receipt = self._purchase_palots(4)
        self._validate_with_backorder(receipt, 52, 2)
        # 2 palots are still to come, which a receipt would propose
        return_picking = self._create_return(receipt, 26)
        self.assertEqual(return_picking.move_ids.purchase_uom_qty, 0)

    def test_line_bought_in_kg_has_no_units_received(self):
        product = self._create_product(
            "Garlic",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        receipt = self._purchase(product, 100, self.uom_kg)
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 0)

    def test_units_received_cannot_be_negative(self):
        receipt = self._purchase_palots(4)
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            receipt.move_ids.purchase_uom_qty = -1
            receipt.move_ids.flush_recordset()

    def test_receipt_form_takes_the_units_received_of_a_dynamic_line(self):
        receipt = self._purchase_palots(4)
        with Form(receipt) as receipt_form:
            with receipt_form.move_ids_without_package.edit(0) as move_form:
                move_form.purchase_uom_qty = 2
        self.assertEqual(receipt.move_ids.purchase_uom_qty, 2)

    def test_receipt_form_hides_the_units_received_of_another_line(self):
        product = self._create_product(
            "Garlic",
            "2000000000015",
            uom_id=self.uom_kg.id,
            uom_po_id=self.uom_kg.id,
        )
        receipt = self._purchase(product, 100, self.uom_kg)
        with Form(receipt) as receipt_form:
            with receipt_form.move_ids_without_package.edit(0) as move_form:
                with self.assertRaisesRegex(
                    AssertionError, "can't write on invisible field 'purchase_uom_qty'"
                ):
                    move_form.purchase_uom_qty = 2

    def test_return_form_hides_the_units_received(self):
        receipt = self._purchase_palots(4)
        self._validate_with_backorder(receipt, 52, 2)
        return_picking = self._create_return(receipt, 26)
        with Form(return_picking) as return_form:
            with return_form.move_ids_without_package.edit(0) as move_form:
                with self.assertRaisesRegex(
                    AssertionError, "can't write on invisible field 'purchase_uom_qty'"
                ):
                    move_form.purchase_uom_qty = 2

    def test_receipt_shows_the_units_received_column(self):
        receipt = self._purchase_palots(4)
        self.assertTrue(self._moves_list_shows_the_column(receipt))

    def test_return_hides_the_units_received_column(self):
        receipt = self._purchase_palots(4)
        self._validate_with_backorder(receipt, 52, 2)
        return_picking = self._create_return(receipt, 26)
        self.assertFalse(self._moves_list_shows_the_column(return_picking))

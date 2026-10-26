# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase, tagged


# post_install: the products created here need the defaults of every installed
# module, and on an update at_install tests run before the modules loaded later
@tagged("post_install", "-at_install")
class TestStockPutawayNoInternal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.write(
            {"groups_id": [(4, cls.env.ref("stock.group_stock_multi_locations").id)]}
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Putaway Warehouse", "code": "PWH"}
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.shelf_location = cls.env["stock.location"].create(
            {"name": "Shelf", "location_id": cls.stock_location.id}
        )
        cls.source_location = cls.env["stock.location"].create(
            {"name": "Source", "location_id": cls.warehouse.view_location_id.id}
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.category = cls.env["product.category"].create({"name": "Putaway"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Putaway Product",
                "is_storable": True,
                "categ_id": cls.category.id,
            }
        )
        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Putaway Product Serial",
                "is_storable": True,
                "tracking": "serial",
                "categ_id": cls.category.id,
            }
        )
        cls.putaway_rule = cls.env["stock.putaway.rule"].create(
            {
                "category_id": cls.category.id,
                "location_in_id": cls.stock_location.id,
                "location_out_id": cls.shelf_location.id,
                "exclude_internal_operations": True,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.source_location, 10
        )

    def test_internal_move_reserve(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.location_dest_id, self.stock_location)

    def test_incoming_move_reserve(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.location_dest_id, self.shelf_location)

    def test_move_without_type_in_internal_picking_reserve(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "picking_id": picking.id,
                "picking_type_id": False,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.assertFalse(move.picking_type_id)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.stock_location)

    def test_move_with_other_type_than_picking_reserve(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "picking_id": picking.id,
                "picking_type_id": self.warehouse.int_type_id.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.stock_location)

    def test_move_without_type_or_picking_reserve(self):
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.shelf_location)

    def test_incoming_move_assign_serial(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_serial.name,
                            "product_id": self.product_serial.id,
                            "product_uom": self.product_serial.uom_id.id,
                            "product_uom_qty": 2,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        # without reserved lines, every generated line looks its location up
        picking.move_ids._do_unreserve()
        picking.move_ids._generate_serial_numbers("001", next_serial_count=2)
        self.assertEqual(picking.move_line_ids.location_dest_id, self.shelf_location)

    def test_internal_move_line_new(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        move_line_form = Form(
            self.env["stock.move.line"].with_context(
                **picking.action_detailed_operations()["context"]
            )
        )
        move_line_form.product_id = self.product
        move_line_form.quantity = 1
        move_line_form.save()
        self.assertEqual(picking.move_line_ids.location_dest_id, self.stock_location)

    def test_internal_move_reserve_first_rule_excludes(self):
        other_shelf_location = self.env["stock.location"].create(
            {"name": "Other Shelf", "location_id": self.stock_location.id}
        )
        self.putaway_rule.sequence = 5
        self.env["stock.putaway.rule"].create(
            {
                "sequence": 10,
                "category_id": self.category.id,
                "location_in_id": self.stock_location.id,
                "location_out_id": other_shelf_location.id,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.location_dest_id, self.stock_location)

    def test_internal_move_reserve_first_rule_applies(self):
        other_shelf_location = self.env["stock.location"].create(
            {"name": "Other Shelf", "location_id": self.stock_location.id}
        )
        self.putaway_rule.sequence = 10
        self.env["stock.putaway.rule"].create(
            {
                "sequence": 5,
                "category_id": self.category.id,
                "location_in_id": self.stock_location.id,
                "location_out_id": other_shelf_location.id,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source_location.id,
                "location_dest_id": self.stock_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.location_dest_id, other_shelf_location)

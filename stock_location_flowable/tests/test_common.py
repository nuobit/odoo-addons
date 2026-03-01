# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import re

from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        cls.picking_type_incoming_1 = cls.env["stock.picking.type"].create(
            {
                "name": "Receipt1",
                "sequence_code": "SEQ-IN",
                "code": "incoming",
                "default_location_dest_id": cls.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
            }
        )

        cls.picking_type_outgoing_1 = cls.env["stock.picking.type"].create(
            {
                "name": "Delivery1",
                "sequence_code": "SEQ-OUT",
                "code": "outgoing",
                "default_location_src_id": cls.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
            }
        )

        cls.picking_type_internal_1 = cls.env["stock.picking.type"].create(
            {
                "name": "InternalTransfer1",
                "sequence_code": "SEQ-INT",
                "code": "internal",
                "default_location_src_id": cls.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
                "default_location_dest_id": cls.env.ref(
                    "stock.stock_location_locations_partner"
                ).id,
            }
        )

        cls.picking_type_mrp_operation_1 = cls.env["stock.picking.type"].create(
            {
                "name": "Production1",
                "sequence_code": "SEQ-MRP",
                "code": "mrp_operation",
            }
        )

        cls.product_flowable_1 = cls.env["product.product"].create(
            {
                "name": "Liquid O2",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_litre").id,
                "uom_po_id": cls.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )

        cls.product_flowable_2 = cls.env["product.product"].create(
            {
                "name": "Liquid N2",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_litre").id,
                "uom_po_id": cls.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )

        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "Warehouse Shelf",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
            }
        )

        cls.location_flowable_1 = cls.env["stock.location"].create(
            {
                "name": "O2 Tank 1",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
                "flowable_storage": True,
                "flowable_capacity": 1000,
                "flowable_uom_id": cls.env.ref("uom.product_uom_litre").id,
                "flowable_allowed_product_ids": [
                    (4, cls.product_flowable_1.id),
                    (4, cls.product_flowable_2.id),
                ],
            }
        )

        cls.flowable_sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Flowable Sequence",
                "code": "test.flowable.sequence",
                "company_id": cls.env.company.id,
            }
        )

        cls.location_flowable_2 = cls.env["stock.location"].create(
            {
                "name": "O2 Tank 2",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
                "flowable_storage": True,
                "flowable_capacity": 1500,
                "flowable_uom_id": cls.env.ref("uom.product_uom_litre").id,
                "flowable_allowed_product_ids": [(4, cls.product_flowable_1.id)],
                "flowable_create_lots": True,
                "flowable_sequence_id": cls.flowable_sequence.id,
            }
        )

        lot_1 = cls.env["stock.production.lot"].create(
            {
                "name": "Lot1",
                "product_id": cls.product_flowable_1.id,
            }
        )

        cls.incoming_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_incoming_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_1.id,
            }
        )

        cls.env["stock.move.line"].create(
            {
                "picking_id": cls.incoming_picking.id,
                "product_id": cls.product_flowable_1.id,
                "product_uom_id": cls.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.incoming_picking.location_dest_id.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.outgoing_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_outgoing_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_1.id,
            }
        )

        cls.env["stock.move.line"].create(
            {
                "picking_id": cls.outgoing_picking.id,
                "product_id": cls.product_flowable_1.id,
                "product_uom_id": cls.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.outgoing_picking.location_dest_id.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.internal_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_internal_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_2.id,
            }
        )

        cls.env["stock.move.line"].create(
            {
                "picking_id": cls.internal_picking.id,
                "product_id": cls.product_flowable_1.id,
                "product_uom_id": cls.product_flowable_1.uom_id.id,
                "lot_id": lot_1.id,
                "qty_done": 10,
                "location_id": cls.env.ref("stock.stock_location_inter_wh").id,
                "location_dest_id": cls.internal_picking.location_dest_id.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.mrp_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_mrp_operation_1.id,
                "location_id": cls.location_flowable_1.id,
                "location_dest_id": cls.location_flowable_2.id,
            }
        )

    def get_error_message_regex(self, str1):
        parts = str1.split("%s")
        escaped_parts = [re.escape(part) for part in parts]
        regex_pattern = ".*".join(escaped_parts)
        return regex_pattern

    def _create_lot(self, product, name):
        return self.env["stock.production.lot"].create(
            {
                "name": name,
                "product_id": product.id,
            }
        )

    def _receive_stock(self, location, product, lot, qty, picking_type=None):
        """Create and validate an incoming picking to any location."""
        if picking_type is None:
            picking_type = self.picking_type_incoming_1
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.supplier_location.id,
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
                "location_id": self.supplier_location.id,
                "location_dest_id": location.id,
                "company_id": self.env.company.id,
            }
        )
        picking.button_validate()
        return picking

    def _create_incoming_picking(self, location, product, lot, qty, picking_type=None):
        """Create an incoming picking WITHOUT validating it."""
        if picking_type is None:
            picking_type = self.picking_type_incoming_1
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.supplier_location.id,
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
                "location_id": self.supplier_location.id,
                "location_dest_id": location.id,
                "company_id": self.env.company.id,
            }
        )
        return picking

    def _find_flowable_production(self, location, picking_type=None):
        if picking_type is None:
            picking_type = self.picking_type_mrp_operation_1
        return self.env["mrp.production"].search(
            [
                ("picking_type_id", "=", picking_type.id),
                ("location_dest_id", "=", location.id),
            ],
            order="id desc",
            limit=1,
        )

    def _get_location_quants(self, location, product):
        return self.env["stock.quant"].search(
            [
                ("location_id", "=", location.id),
                ("product_id", "=", product.id),
            ]
        )

    def _get_positive_quantity(self, location, product):
        quants = self._get_location_quants(location, product)
        return sum(quants.filtered(lambda q: q.quantity > 0).mapped("quantity"))

    def _seed_flowable_location(
        self, location, product, lot, qty, picking_type=None, mrp_picking_type=None
    ):
        """Receive initial stock and complete the resulting MO."""
        picking = self._receive_stock(
            location, product, lot, qty, picking_type=picking_type
        )
        production = self._find_flowable_production(
            location, picking_type=mrp_picking_type
        )
        if production:
            production.button_mark_done()
        return picking

    def _create_inventory_adjustment(self, location, product, lot, qty):
        """Create and validate a simple inventory adjustment (1 lot)."""
        inventory = self.env["stock.inventory"].create(
            {"name": f"Adjust {product.name} at {location.name}"}
        )
        inventory.action_start()
        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": location.id,
                "prod_lot_id": lot.id,
                "product_qty": qty,
            }
        )
        inventory.action_validate()
        return inventory

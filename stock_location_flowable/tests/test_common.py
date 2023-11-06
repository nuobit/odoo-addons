# Copyright NuoBiT Solutions - Frank Cespedes <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import re

from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

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
                "name": "ProductFlowable1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_litre").id,
                "uom_po_id": cls.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )

        cls.product_flowable_2 = cls.env["product.product"].create(
            {
                "name": "ProductFlowable2",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_litre").id,
                "uom_po_id": cls.env.ref("uom.product_uom_litre").id,
                "tracking": "lot",
            }
        )

        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "Location1",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
            }
        )

        cls.location_flowable_1 = cls.env["stock.location"].create(
            {
                "name": "LocationFlowable1",
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

        cls.location_flowable_2 = cls.env["stock.location"].create(
            {
                "name": "LocationFlowable2",
                "usage": "internal",
                "location_id": cls.env.ref("stock.stock_location_locations_partner").id,
                "flowable_storage": True,
                "flowable_capacity": 1500,
                "flowable_uom_id": cls.env.ref("uom.product_uom_litre").id,
                "flowable_allowed_product_ids": [(4, cls.product_flowable_1.id)],
                "flowable_create_lots": True,
                "flowable_sequence_id": cls.env.ref("stock.sequence_tracking").id,
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
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
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
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
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

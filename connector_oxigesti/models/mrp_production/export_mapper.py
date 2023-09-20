# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    follow_m2o_relations,
    mapping,
    none,
    only_create,
)


class MrpProductionExportMapper(Component):
    _name = "oxigesti.mrp.production.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.mrp.production"

    direct = [
        (none("date_planned_start"), "FechaProduccion"),
        (none(follow_m2o_relations("lot_producing_id.name")), "LoteBotellaVacia"),
        (none(follow_m2o_relations("product_id.code")), "CodigoBotellaVacia"),
    ]

    @only_create
    @mapping
    def CodigoOrdenProduccion(self, record):
        return {"CodigoOrdenProduccion": record.name}

    @mapping
    def EsMontaje(self, record):
        unbuild_count = self.env["mrp.unbuild"].search_count(
            [("mo_id", "=", record.odoo_id.id), ("state", "=", "done")]
        )
        return {"EsMontaje": 0 if unbuild_count > 1 else 1}

    @mapping
    def Codigo(self, record):
        cylinder_product = record.move_raw_ids.product_id.filtered(
            lambda x: x.mrp_type == "cylinder"
        )
        valve_product = record.move_raw_ids.product_id.filtered(
            lambda x: x.mrp_type == "valve"
        )
        if len(cylinder_product) == 0 or len(valve_product) == 0:
            raise AssertionError(
                "Production of empty gas bottle type without"
                " cylinder or valve product: %s" % record.name
            )
        if len(cylinder_product) > 1 or len(valve_product) > 1:
            raise AssertionError(
                "Production of empty gas bottle type with"
                " more than one cylinder or valve product: %s" % record.name
            )
        return {
            "CodigoCilindro": cylinder_product.code,
            "CodigoValvula": valve_product.code,
        }

    @mapping
    def Lote(self, record):
        cylinder_mr = record.move_raw_ids.filtered(
            lambda x: x.product_id.mrp_type == "cylinder" and x.quantity_done > 0
        )
        valve_mr = record.move_raw_ids.filtered(
            lambda x: x.product_id.mrp_type == "valve" and x.quantity_done > 0
        )
        if (
            len(cylinder_mr) > 1
            or len(valve_mr) > 1
            or sum(cylinder_mr.mapped("quantity_done")) > 1
            or sum(valve_mr.mapped("quantity_done")) > 1
        ):
            raise AssertionError(
                "The empty gas bottle (%s) has been created with"
                " more than one valve or cylinder" % record.name
            )
        if len(cylinder_mr.move_line_ids) > 1 or len(valve_mr.move_line_ids) > 1:
            raise AssertionError(
                "You have a component with more than one serial"
                " number to generate: %s" % record.name
            )
        return {
            "LoteCilindro": cylinder_mr.move_line_ids.lot_id.name or None,
            "LoteValvula": valve_mr.move_line_ids.lot_id.name or None,
        }

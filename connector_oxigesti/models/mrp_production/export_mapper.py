# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import follow_m2o_relations, mapping, none


class MrpProductionExportMapper(Component):
    _name = "oxigesti.mrp.production.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.mrp.production"

    direct = [
        ("name", "CodigoOrdenProduccion"),
        (none("date_planned_start"), "FechaProduccion"),
        (none(follow_m2o_relations("lot_producing_id.name")), "LoteBotellaVacia"),
    ]

    @mapping
    def CodigoBotellaVacia(self, record):
        if not record.product_id.default_code:
            raise ValidationError(
                _("Internal Reference not set in product: %s") % record.product_id.name
            )
        return {"CodigoBotellaVacia": record.product_id.default_code}

    @mapping
    def EsMontaje(self, record):
        unbuild_count = self.env["mrp.unbuild"].search(
            [("mo_id", "=", record.odoo_id.id), ("state", "=", "done")]
        )
        if len(unbuild_count) > 1:
            raise ValidationError(
                _("The production %s has more than one unbuild. %s")
                % (record.name, unbuild_count.mapped("name"))
            )
        return {"EsMontaje": 0 if len(unbuild_count) > 0 else 1}

    @mapping
    def Componentes(self, record):
        binder = self.binder_for("oxigesti.mrp.production")
        mrp_production = binder.unwrap_binding(record)
        move_raws = mrp_production._get_valid_components()
        mrp_type_map = {
            "cylinder": ("CodigoCilindro", "LoteCilindro"),
            "valve": ("CodigoValvula", "LoteValvula"),
        }
        res = {}
        for move_raw in move_raws:
            mrp_type = move_raw.product_id.mrp_type
            if mrp_type not in mrp_type_map:
                raise ValidationError(_("Invalid product type: %s") % mrp_type)
            default_code = move_raw.product_id.default_code
            if not default_code:
                raise ValidationError(
                    _("Internal Reference not set in product: %s")
                    % move_raw.product_id.name
                )
            lot = move_raw.move_line_ids.lot_id
            if not lot:
                raise ValidationError(
                    _("Serial Number not set in product: %s") % move_raw.product_id.name
                )
            code_key, lot_key = mrp_type_map[mrp_type]
            res[code_key] = default_code
            res[lot_key] = lot.name
        return res

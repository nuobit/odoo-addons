# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class OxigestiSPMSSaleOrderImportMapChild(Component):
    _name = "lengow.sale.order.map.child.import"
    _inherit = "oxigesti.spms.map.child.import"

    _apply_on = "oxigesti.spms.sale.order.line"

    # def get_item_values(self, map_record, to_attr, options):
    #     binder = self.binder_for("oxigesti.spms.sale.order.line")
    #     external_id = binder.dict2id(map_record.source, in_field=False)
    #     oxigesti_spms_order_line = binder.to_internal(external_id, unwrap=False)
    #
    #     if oxigesti_spms_order_line:
    #         map_record.update(id=oxigesti_spms_order_line.id)
    #
    #     return map_record.values(**options)

    # TODO: Put in a superclass
    def format_items(self, items_values):
        ops = []

        for values in items_values:
            _id = values.pop("id", None)
            if _id:
                ops.append((1, _id, values))
            else:
                ops.append((0, False, values))
        return ops


class OxigestiSpmsSaleOrderImporterMapper(Component):
    _name = "oxigesti.spms.sale.order.importer.mapper"
    _inherit = "oxigesti.spms.import.mapper"

    _apply_on = "oxigesti.spms.sale.order"
    _usage = "import.mapper"

    direct = [
        ("DataFim", "date_order"),
        ("Invoice_Id", "client_order_ref"),
    ]

    children = [
        ("lines", "oxigesti_spms_order_lines_ids", "oxigesti.spms.sale.order.line")
    ]

    @changed_by("partner_id")
    @mapping
    def partner_id(self, record):

        binder = self.binder_for("oxigesti.spms.res.partner")
        external_id = record["UnidadeLocalSalude"]

        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
            "partner_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )
        return {"partner_id": partner.id}

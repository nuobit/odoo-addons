# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class OxigestiSpmsSaleOrderExportMapper(Component):
    _name = "oxigesti.spms.sale.order.export.mapper"
    _inherit = "oxigesti.spms.export.mapper"
    _apply_on = "oxigesti.spms.sale.order"

    @mapping
    def Odoo_Numero_Albaran(self, record):
        if record.state in ["sale", "done"]:
            return {"Odoo_Numero_Albaran": record["name"]}
        else:
            return

    @mapping
    def Odoo_Fecha_Generado_Albaran(self, record):
        if record.state in ["sale", "done"]:
            return {"Odoo_Fecha_Generado_Albaran": record["date_order"]}
        else:
            return

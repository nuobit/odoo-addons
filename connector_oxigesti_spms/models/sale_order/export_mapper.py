# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSpmsSaleOrderExportMapper(Component):
    _name = "oxigesti.spms.sale.order.export.mapper"
    _inherit = "oxigesti.spms.export.mapper"
    _apply_on = "oxigesti.spms.sale.order"

    direct = [
        ("name", "Odoo_Numero_Albaran"),
        ("date_order", "Odoo_Fecha_Generado_Albaran"),
    ]

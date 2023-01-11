# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderExportMapper(Component):
    _name = "oxigesti.sale.order.export.mapper"
    _inherit = "oxigesti.export.mapper"

    _apply_on = "oxigesti.sale.order"

    direct = [
        ("name", "Odoo_Numero_Albaran"),
        ("date_order", "Odoo_Fecha_Generado_Albaran"),
    ]

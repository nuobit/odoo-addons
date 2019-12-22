# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class SaleOrderLineAdapter(Component):
    _name = 'oxigesti.sale.order.line.adapter'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.sale.order.line'

    _sql = """select l.Codigo_Servicio, l.CodigoArticulo, l.Partida,
                     l.Cantidad
              from %(schema)s.Odoo_Servicios_Cargos l

        """

    _id = ('Codigo_Servicio', 'CodigoArticulo', 'Partida')

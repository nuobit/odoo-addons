# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class SaleOrderLineAdapter(Component):
    _name = 'ambugest.sale.order.line.adapter'
    _inherit = 'ambugest.adapter'
    _apply_on = 'ambugest.sale.order.line'

    _sql = """select c.EMPRESA,  
                     l.Fecha_Servicio, l.Codigo_Servicio, l.Servicio_Dia, l.Servicio_Ano,
                     l.Articulo,
                     l.Cantidad, l.Importe, l.Total
              from %(schema)s.Odoo_Servicios_Cargos l, %(schema)s.Odoo_Servicios s, 
                   %(schema)s."Unidades productivas" c
              where l.Fecha_Servicio = s.Fecha_Servicio and 
                    l.Codigo_Servicio = s.Codigo_Servicio and 
                    l.Servicio_Dia = s.Servicio_Dia and 
                    l.Servicio_Ano = s.Servicio_Ano and
                    cast(c."Codi UP" as integer) >= 90000 and
                    s.Cliente = c.Cliente
    """

    _id = ('EMPRESA', 'Fecha_Servicio', 'Codigo_Servicio', 'Servicio_Dia', 'Servicio_Ano',
           'Articulo')

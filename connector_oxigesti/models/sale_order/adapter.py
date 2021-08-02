# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderAdapter(Component):
    _name = 'oxigesti.sale.order.adapter'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.sale.order'

    _sql = """select s.Codigo_Servicio, s.Codigo_Mutua, s.Fecha_Servicio, 
                     s.Referencia_de_la_Mutua,
                     s.Fecha_Modifica, 
                     s.Odoo_Numero_Albaran
              from %(schema)s.Odoo_Servicios s
              where s.Odoo_Verificado = 1
            """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Servicios s
                     where s.Codigo_Servicio = %%(Codigo_Servicio)s
                """

    _id = ('Codigo_Servicio',)

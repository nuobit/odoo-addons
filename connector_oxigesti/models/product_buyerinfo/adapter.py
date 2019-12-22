# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class ProductBuyerinfoAdapter(Component):
    _name = 'oxigesti.product.buyerinfo.adapter'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.product.buyerinfo'

    _sql = """select b.CodigoArticulo, b.Codigo_Mutua, b.Descripcion_Cliente
              from %(schema)s.Odoo_Articulos_por_Clientes b
            """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Articulos_por_Clientes s
                     where s.CodigoArticulo = %%(CodigoArticulo)s and
                           s.Codigo_Mutua = %%(Codigo_Mutua)s
                """

    _sql_insert = """insert into %(schema)s.Odoo_Articulos_por_Clientes 
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
                """

    _id = ('CodigoArticulo', 'Codigo_Mutua')

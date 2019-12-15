# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class ProductPricelistItemAdapter(Component):
    _name = 'oxigesti.product.pricelist.item.adapter'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.product.pricelist.item'

    _sql = """select b.IdArticulo, b.IdCliente, b.Importe
              from %(schema)s.Odoo_Articulos_Generales_x_Cliente b
            """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Articulos_Generales_x_Cliente s
                     where s.IdArticulo = %%(IdArticulo)s and
                           s.IdCliente = %%(IdCliente)s
                """

    _sql_insert = """insert into %(schema)s.Odoo_Articulos_Generales_x_Cliente 
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
                """

    _id = ('IdArticulo', 'IdCliente')

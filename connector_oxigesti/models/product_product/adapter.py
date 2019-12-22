# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class ProductProductAdapter(Component):
    _name = 'oxigesti.product.product'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.product.product'

    _sql = """select a.CodigoArticulo, a.DescripcionArticulo, a.Familia, a.CodigoAlternativo, a.Importe
              from %(schema)s.Odoo_Articulos_Generales a
           """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Articulos_Generales s
                     where s.CodigoArticulo = %%(CodigoArticulo)s
         """

    _sql_insert = """insert into %(schema)s.Odoo_Articulos_Generales 
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
         """

    _id = ('CodigoArticulo',)

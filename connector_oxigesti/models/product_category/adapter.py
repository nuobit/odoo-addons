# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ProductCategoryAdapter(Component):
    _name = 'oxigesti.product.category.adapter'
    _inherit = 'oxigesti.adapter'

    _apply_on = 'oxigesti.product.category'

    _sql = """select b.Id, b.IdCategoriaOdoo, b.Descripcion
              from %(schema)s.Odoo_Articulos_Categorias b
              where b.Eliminado = 0
            """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Articulos_Categorias s
                     where s.Id = %%(Id)s
                """

    _sql_insert = """insert into %(schema)s.Odoo_Articulos_Categorias 
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
                """

    _sql_delete = """delete from %(schema)s.Odoo_Articulos_Categorias
                     where Id = %%(Id)s
         """

    _id = ('Id',)

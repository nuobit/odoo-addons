# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class StockProductionLotAdapter(Component):
    _name = "oxigesti.stock.production.lot.adapter"
    _inherit = "oxigesti.adapter"

    _apply_on = "oxigesti.stock.production.lot"

    _sql = """select l.CodigoArticulo, l.Lote
              from %(schema)s.Odoo_Articulos_Lotes l
            """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Articulos_Lotes s
                     where s.CodigoArticulo = %%(CodigoArticulo)s and
                           s.Lote = %%(Lote)s
                """

    _sql_insert = """insert into %(schema)s.Odoo_Articulos_Lotes
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
                """

    _id = ("CodigoArticulo", "Lote")

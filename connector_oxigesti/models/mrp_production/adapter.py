# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class MrpProductionAdapter(Component):
    _name = "oxigesti.mrp.production.adapter"
    _inherit = "oxigesti.adapter"

    _apply_on = "oxigesti.mrp.production"

    _sql = """select a.Id, a.CodigoOrdenProduccion, a.FechaProduccion,
                     a.CodigoOrdenDeconstruccion, a.CodigoBotellaVacia,
                     a.LoteBotellaVacia, a.CodigoCilindro, a.LoteCilindro,
                     a.CodigoValvula, a.LoteValvula
              from %(schema)s.Odoo_Orden_Produccion a
           """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Orden_Produccion s
                     where s.CodigoOrdenProduccion = %%(CodigoOrdenProduccion)s
         """

    _sql_insert = """insert into %(schema)s.Odoo_Orden_Produccion
                         (%(fields)s)
                     output %(retvalues)s
                     values (%(phvalues)s)
         """

    _id = ("Id",)

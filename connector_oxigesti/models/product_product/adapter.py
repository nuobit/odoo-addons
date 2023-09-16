# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductProductAdapter(Component):
    _name = "oxigesti.product.product.adapter"
    _inherit = "oxigesti.adapter"

    _apply_on = "oxigesti.product.product"

    _sql = """select a.CodigoArticulo, a.DescripcionArticulo,
              a.Familia, a.CodigoAlternativo, a.Importe, a.Diametro,
              a.ColorOjiva, a.AlojamientoValvula, a.Base,
              a.CapacidadGeometrica, a.ColorCuerpo, a.PresionPrueba,
              a.RoscaCollarinParaTulipa, a.TipoAleacion,
              a.AcoplamientoSalida, a.PresionMaximaTrabajo, a.Sonda,
              a.TomaRapida, a.Cromada, a.TipoValvula, a.PresionResidual,
              a.CaudalPresionMaximo, a.PresionRotura, a.Comunicacion, a.Manometro
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

    _sql_delete = """delete from %(schema)s.Odoo_Articulos_Generales
                     where CodigoArticulo = %%(CodigoArticulo)s
         """

    _id = ("CodigoArticulo",)

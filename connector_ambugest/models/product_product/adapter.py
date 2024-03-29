# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class ProductProductAdapter(Component):
    _name = "ambugest.product.product"
    _inherit = "ambugest.adapter"
    _apply_on = "ambugest.product.product"

    _sql = """select a.Id, a.Articulo, a.Odoo_Articulo, 1 as Empresa,
                     a.Traslado, a.Kms, a.Horas_Medico_4ph, a.Horas_DUE_4ph, a.Horas_Espera
              from  %(schema)s.Odoo_Articulos_Generales a
              union all
              select a.Id, a.Articulo, a.Odoo_Articulo, 2 as Empresa,
                     a.Traslado, a.Kms, a.Horas_Medico_4ph, a.Horas_DUE_4ph, a.Horas_Espera
              from  %(schema)s.Odoo_Articulos_Generales a
     """
    _id = ("Empresa", "Id")

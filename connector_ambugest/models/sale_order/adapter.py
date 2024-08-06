# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class SaleOrderAdapter(Component):
    _name = "ambugest.sale.order.adapter"
    _inherit = "ambugest.adapter"
    _apply_on = "ambugest.sale.order"

    _sql = """select c.EMPRESA,  c."Codi UP" as "CodiUP",
                     s.Fecha_Servicio, s.Hora_Servicio, s.Codigo_Servicio,
                     s.Servicio_Dia, s.Servicio_Ano, s.Fecha_Modifica,
                     s.Num_Contrato, s.Nombre_Asegurado, s.DNI_Asegurado,
                     s.Num_Asegurado, a.Codigo_Aseguradora, a.Nombre_Aseguradora,
                     s.Referencia_autorizacion, s.Clave, s.Motivo_Trasladado,
                     s.Matricula, s.Origen, s.Destino,
                     s.Codigo_Ida_y_Vuelta, s.Servicio_de_vuelta
              from %(schema)s.Odoo_Servicios s
                    left join %(schema)s.Odoo_Aseguradoras_por_Clientes a on
                       s.Cliente = a.Cliente and s.Cliente_Aseguradora = a.Codigo_Aseguradora,
                   %(schema)s."Unidades productivas" c
              where c."Activa_en_AmbuGEST" = 1 and
                    cast(c."Codi UP" as integer) >= 90000 and
                    s.Cliente = c.Cliente and
                    s.Odoo_Verificado = 1 and
                    s.Odoo_Numero_Albaran is null
     """

    _sql_update = """update s
                     set %(qset)s
                     from %(schema)s.Odoo_Servicios s, %(schema)s."Unidades productivas" c
                     where c."Activa_en_AmbuGEST" = 1 and
                           cast(c."Codi UP" as integer) >= 90000 and
                           s.Cliente = c.Cliente and

                           c.EMPRESA = %%(EMPRESA)s and
                           c."Codi UP" = %%(CodiUP)s and
                           s.Fecha_Servicio = %%(Fecha_Servicio)s and
                           s.Codigo_Servicio = %%(Codigo_Servicio)s and
                           s.Servicio_Dia = %%(Servicio_Dia)s and
                           s.Servicio_Ano = %%(Servicio_Ano)s
         """

    _id = (
        "EMPRESA",
        "CodiUP",
        "Fecha_Servicio",
        "Codigo_Servicio",
        "Servicio_Dia",
        "Servicio_Ano",
    )

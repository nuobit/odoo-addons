# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class SaleOrderAdapter(Component):
    _name = 'ambugest.sale.order.adapter'
    _inherit = 'ambugest.adapter'
    _apply_on = 'ambugest.sale.order'

    _sql = """select c.EMPRESA,  c."Codi UP" as "CodiUP",
                     s.Fecha_Servicio, s.Codigo_Servicio, s.Servicio_Dia, s.Servicio_Ano,
                     s.Fecha_Modifica,

                     s.Num_Contrato, s.Nombre_Asegurado, s.DNI_Asegurado,
                         s.Num_Asegurado,s.Referencia_autorizacion,
                     s.Matricula, s.Origen, s.Destino, s.Servicio_de_vuelta
              from %(schema)s.Odoo_Servicios s, %(schema)s."Unidades productivas" c
              where c."Activa_en_AmbuGEST" = 1 and
                    cast(c."Codi UP" as integer) >= 90000 and
                    s.Cliente = c.Cliente and
                    s.Odoo_Verificado = 1
     """
    _id = ('EMPRESA', 'CodiUP', 'Fecha_Servicio', 'Codigo_Servicio', 'Servicio_Dia', 'Servicio_Ano')

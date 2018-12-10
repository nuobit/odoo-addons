# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job

import pymssql


class HrEmployeeAdapter(Component):
    _name = 'sage.hr.employee'
    _inherit = 'sage.adapter'
    _apply_on = 'sage.hr.employee'

    _sql = """select e.CodigoEmpresa, e.CodigoEmpleado, e.SiglaNacion, e.Dni, e.FechaAlta, 
                     e.IdEmpleado, p.RazonSocialEmpleado, 
                     p.NombreEmpleado, p.PrimerApellidoEmpleado, p.SegundoApellidoEmpleado,
                     p.NumeroHijos, p.Sexo, p.EstadoCivil, p.FechaNacimiento, p.Profesion,
                     p.Email1, p.Email2
              from  %(schema)s.empleadonomina e, %(schema)s.personas p 
              where e.SiglaNacion = p.SiglaNacion and
                    e.Dni = p.Dni and
                    not exists (
                       select 1
                       from %(schema)s.empleadonomina e1
                       where e.CodigoEmpresa = e1.CodigoEmpresa and 
                             e.CodigoEmpleado = e1.CodigoEmpleado and
                             e.FechaAlta < e1.FechaAlta
                    )
     """
    _id = ('CodigoEmpresa', 'CodigoEmpleado')
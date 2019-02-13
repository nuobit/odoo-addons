# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class PayslipCheckAdapter(Component):
    _name = 'sage.payroll.sage.payslip.check.adapter'
    _inherit = 'sage.adapter'

    _apply_on = 'sage.payroll.sage.payslip.check'

    _sql = """select e.CodigoEmpresa, e.CodigoEmpleado,
                     e.Año, e.MesD, e.CodigoConvenio, e.FechaRegistroCV,
                     e.FechaCobro,
                     sum(e.ImporteFijo) as ImporteFijo
              from (select ec.CodigoEmpresa, ec.CodigoEmpleado, ec.OrdenNom,
                           h.Año, h.MesD, c.CodigoConvenio, c.FechaRegistroCV,
                           h.FechaCobro,
                           ec.ImporteFijo
                    from EmpleadoCobro ec, Historico h, ConvenioConcepto c
                    where ec.CodigoFormaCobro = 'TAL' AND
                          ec.ImporteFijo != 0  and
                          h.CodigoEmpresa in (1, 2, 4, 5) AND
                          h.Año >= 2018 AND
                          h.TotalFichaHistorica in ('TD1', 'TR1') AND
                          h.CodigoConceptoNom = c.CodigoConceptoNom AND
                          h.CodigoEmpresa = c.CodigoEmpresa AND
                
                          ec.CodigoEmpresa = h.CodigoEmpresa and
                          ec.IdEmpleado = h.IdEmpleado and
                          ec.CodigoEmpleado = h.CodigoEmpleado 
                    group by ec.CodigoEmpresa, ec.CodigoEmpleado, ec.OrdenNom,
                             h.Año, h.MesD, c.CodigoConvenio, c.FechaRegistroCV,
                             h.FechaCobro,
                             ec.ImporteFijo
                  ) e
              group by e.CodigoEmpresa, e.CodigoEmpleado, e.OrdenNom,
                       e.Año, e.MesD, e.CodigoConvenio, e.FechaRegistroCV,
                       e.FechaCobro
    """

    _id = ('CodigoEmpresa', 'CodigoEmpleado',
           'Año', 'MesD', 'CodigoConvenio', 'FechaRegistroCV', 'FechaCobro')

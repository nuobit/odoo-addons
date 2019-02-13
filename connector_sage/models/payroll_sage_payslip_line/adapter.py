# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class PayslipLineAdapter(Component):
    _name = 'sage.payroll.sage.payslip.line.adapter'
    _inherit = 'sage.adapter'
    _apply_on = 'sage.payroll.sage.payslip.line'


    _sql = """select n.CodigoEmpresa, n.CodigoEmpleado, n.IdEmpleado,
                        n.Año, n.MesD, n.CodigoConceptoNom, 
                        n.TipoProceso,n.ClaveEspecial,
                        n.ConceptoCorto, n.ConceptoLargo,
                        n.FechaCobro,
                     c.CodigoConvenio, c.FechaRegistroCV,
                     sum(n.ImporteNom) as ImporteNom
              from Historico n, ConvenioConcepto c
              where n.CodigoEmpresa in (1, 2, 4, 5) AND
                    n.Año >= 2018 AND
                    n.CodigoConceptoNom = c.CodigoConceptoNom AND
                    n.CodigoEmpresa = c.CodigoEmpresa
              group by n.CodigoEmpresa, n.CodigoEmpleado, n.IdEmpleado,
                       n.Año, n.MesD, n.CodigoConceptoNom, 
                       n.TipoProceso,n.ClaveEspecial,
                       n.ConceptoCorto, n.ConceptoLargo,
                       n.FechaCobro,
                       c.CodigoConvenio, c.FechaRegistroCV
              having sum(n.importenom) != 0
    """

    _id = ('CodigoEmpresa', 'Año', 'MesD', 'CodigoEmpleado', 'CodigoConceptoNom',
           'CodigoConvenio', 'FechaRegistroCV')
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipLineTransferAdapter(Component):
    _name = "sage.payroll.sage.payslip.line.transfer.adapter"
    _inherit = "sage.payroll.sage.payslip.line.adapter"

    _apply_on = "sage.payroll.sage.payslip.line.transfer"

    _sql = """select n.CodigoEmpresa, n.Año, n.MesD,
                     n.TipoProceso,
                     n.CodigoEmpleado, n.CodigoConceptoNom,
                     c.CodigoConvenio, c.FechaRegistroCV,
                     n.FechaCobro,
                     min(n.ConceptoLargo) as ConceptoLargo,
                     sum(n.ImporteNom) as ImporteNom
              from Historico n, ConvenioConcepto c
              where n.CodigoEmpresa in (1, 2, 4, 5) AND
                    n.Año >= 2018 AND
                    n.TotalFichaHistorica in ('TD1', 'TR1') AND
                    n.CodigoConceptoNom = c.CodigoConceptoNom AND
                    n.CodigoEmpresa = c.CodigoEmpresa
              group by n.CodigoEmpresa, n.Año, n.MesD,
                       n.TipoProceso,
                       n.CodigoEmpleado, n.CodigoConceptoNom,
                       c.CodigoConvenio, c.FechaRegistroCV,
                       n.FechaCobro
              having sum(n.importenom) != 0
    """

    _id = (
        "CodigoEmpresa",
        "Año",
        "MesD",
        "TipoProceso",
        "CodigoEmpleado",
        "CodigoConceptoNom",
        "CodigoConvenio",
        "FechaRegistroCV",
        "FechaCobro",
    )

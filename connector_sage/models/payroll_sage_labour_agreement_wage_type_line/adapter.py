# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayrollSageLabourAgreementWageTypeLineAdapter(Component):
    _name = "sage.payroll.sage.labour.agreement.wage.type.line.adapter"
    _inherit = "sage.adapter"
    _apply_on = "sage.payroll.sage.labour.agreement.wage.type.line"

    _sql = """select c.CodigoEmpresa, c.CodigoConvenio, c.FechaRegistroCV, c.CodigoConceptoNom,
                     c.ConceptoCorto, c.ConceptoLargo,
                     c.Positivo, c.TotalFichaHistorica, c.CasillaRos, c.DevRet,
                     c.CotizacionSegSoc, c.CotizacionIrpf
              from %(schema)s.ConvenioConcepto c, %(schema)s.Convenio n
              where c.CodigoConvenio = n.CodigoConvenio and
                    c.FechaRegistroCV = n.FechaRegistroCV
     """
    _id = ("CodigoEmpresa", "CodigoConvenio", "FechaRegistroCV", "CodigoConceptoNom")

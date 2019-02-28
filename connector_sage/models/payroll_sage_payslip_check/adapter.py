# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component


class PayslipCheckAdapter(Component):
    _name = 'sage.payroll.sage.payslip.check.adapter'
    _inherit = 'sage.adapter'

    _apply_on = 'sage.payroll.sage.payslip.check'

    _sql = """select ec.CodigoEmpresa, ec.CodigoEmpleado, 
                     ec.Año, ec.MesD, CAST(ec.IdEmpleado AS char(36)) as IdEmpleado, ec.OrdenNom, 
                     ec.Importe
              from HistoricoRelacionesDePago ec
              where ec.CodigoFormaCobro = 'TAL' and 
                    ec.TipoProceso = 'MES'
    """

    _id = ('CodigoEmpresa', 'CodigoEmpleado', 'Año', 'MesD',
           'IdEmpleado', 'OrdenNom')

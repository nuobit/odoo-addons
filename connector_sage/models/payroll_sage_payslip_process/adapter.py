# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayrollSagePayslipProcessAdapter(Component):
    _name = "sage.payroll.sage.payslip.process.adapter"
    _inherit = "sage.adapter"
    _apply_on = "sage.payroll.sage.payslip.process"

    _sql = """
        select n.CodigoEmpresa,
               n.TipoProceso
        from %(schema)s.Historico n
        where n.TipoProceso is not null
          and n.TipoProceso != ''
        group by n.CodigoEmpresa,
                 n.TipoProceso
    """

    _id = ("CodigoEmpresa", "TipoProceso")

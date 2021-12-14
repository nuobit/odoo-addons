# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class PayslipCheckAdapter(Component):
    _name = "sage.payroll.sage.payslip.check.adapter"
    _inherit = "sage.adapter"

    _apply_on = "sage.payroll.sage.payslip.check"

    _sql = """select ec.CodigoEmpresa, ec.CodigoEmpleado,
                     ec.Año, ec.MesD, ec.TipoProceso,
                     CAST(ec.IdEmpleado AS char(36)) as IdEmpleado, ec.OrdenNom,
                     ec.Importe,
                     coalesce(en.FechaBaja, convert(datetime2, '3000-12-31 00:00:00')) as FechaBaja
              from HistoricoRelacionesDePago ec, EmpleadoNomina en
              where ec.CodigoEmpresa = en.CodigoEmpresa AND
                    ec.IdEmpleado = en.IdEmpleado AND
                    ec.CodigoFormaCobro = 'TAL'
    """

    _id = (
        "CodigoEmpresa",
        "CodigoEmpleado",
        "Año",
        "MesD",
        "TipoProceso",
        "IdEmpleado",
        "OrdenNom",
    )

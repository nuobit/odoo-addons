# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
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
                     coalesce(en.FechaBaja,
                     convert(datetime2, '3000-12-31 00:00:00')) as FechaBaja
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

    # The checks follow the transfer lines: a filter on these columns of the
    # transfer lines selects the checks of the employees with transfer lines
    # that meet it in the same month and process
    _transfer_line_columns = ("CodigoConvenio", "FechaRegistroCV", "FechaCobro")

    def _get_where(self, filters):
        where, values = super()._get_where(
            {
                column: value
                for column, value in filters.items()
                if column not in self._transfer_line_columns
            }
        )
        line_filters = {
            "l.%s" % column: value
            for column, value in filters.items()
            if column in self._transfer_line_columns
        }
        if line_filters:
            line_adapter = self.component(
                usage="backend.adapter",
                model_name="sage.payroll.sage.payslip.line.transfer",
            )
            line_where, line_values = line_adapter._get_where(line_filters)
            where.append(
                "exists (select 1 from (%s) l "
                "where l.CodigoEmpresa = t.CodigoEmpresa and "
                "l.CodigoEmpleado = t.CodigoEmpleado and "
                "l.Año = t.Año and l.MesD = t.MesD and "
                "l.TipoProceso = t.TipoProceso and %s)"
                % (
                    line_adapter._sql % dict(schema=self.schema),
                    " and ".join(line_where),
                )
            )
            values += line_values
        return where, values

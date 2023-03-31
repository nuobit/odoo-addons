# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector_sage.components.adapter import (  # pylint: disable=W7950
    GenericAdapter,
)


class PayrollSageLabourAgreementAdapter(Component):
    _name = "sage.payroll.sage.labour.agreement.adapter"
    _inherit = "sage.adapter"
    _apply_on = "sage.payroll.sage.labour.agreement"

    _sql = """
        select *
        from (%(sql_convenios)s) n
        where exists (
            select 1
            from %%(schema)s.ConvenioConcepto c
            where c.CodigoEmpresa = n.CodigoEmpresa and
                  c.CodigoConvenio = n.CodigoConvenio and
                  c.FechaRegistroCV = n.FechaRegistroCV
            )
     """ % {
        "sql_convenios": GenericAdapter._sql_convenios
    }

    _id = ("CodigoEmpresa", "CodigoConvenio", "FechaRegistroCV")

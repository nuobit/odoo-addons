# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class PayrollSagePayslipProcessImportMapper(Component):
    _name = "sage.payroll.sage.payslip.process.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.payroll.sage.payslip.process"

    direct = [
        ("TipoProceso", "name"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("TipoProceso", "sage_tipo_proceso"),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

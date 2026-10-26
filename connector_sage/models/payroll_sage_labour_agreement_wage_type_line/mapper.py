# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class PayrollSageLabourAgreementWageTypeLineImportMapper(Component):
    _name = "sage.payroll.sage.labour.agreement.wage.type.line.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.payroll.sage.labour.agreement.wage.type.line"

    direct = [
        ("CodigoConceptoNom", "code"),
        ("ConceptoCorto", "short_name"),
        ("ConceptoLargo", "name"),
        ("Positivo", "positive"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("CodigoConvenio", "sage_codigo_convenio"),
        ("FechaRegistroCV", "sage_fecha_registro_cv"),
        ("CodigoConceptoNom", "sage_codigo_concepto_nom"),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def total_historical_record(self, record):
        mapping = {
            "TD1": "accrural",
            "TR1": "withholding",
            "NO": "no",
        }
        value = None

        value0 = record["TotalFichaHistorica"]
        if value0 in mapping:
            value = mapping[value0]

        return {"total_historical_record": value}

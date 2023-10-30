# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class PayrollSageLabourAgreementImportMapper(Component):
    _name = "sage.payroll.sage.labour.agreement.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.payroll.sage.labour.agreement"

    direct = [
        ("Convenio", "name"),
        ("CodigoConvenio", "code"),
        ("FechaRegistroCV", "registration_date_cv"),
        ("FechaFinalNom", "end_date"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("CodigoConvenio", "sage_codigo_convenio"),
        ("FechaRegistroCV", "sage_fecha_registro_cv"),
    ]

    def _get_wage_type_lines(self, record, model_name):
        adapter = self.component(usage="backend.adapter", model_name=model_name)
        lines = adapter.search(
            filters={
                "CodigoEmpresa": record["CodigoEmpresa"],
                "CodigoConvenio": record["CodigoConvenio"],
                "FechaRegistroCV": record["FechaRegistroCV"],
            }
        )

        return lines

    children = [
        (
            _get_wage_type_lines,
            "sage_wage_type_line_ids",
            "sage.payroll.sage.labour.agreement.wage.type.line",
        ),
    ]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        source = map_record.source
        # TODO patch ImportMapper in connector to support callable
        if callable(from_attr):
            child_records = from_attr(self, source, model_name)
        else:
            child_records = source[from_attr]

        children = []
        for child_record in child_records:
            adapter = self.component(usage="backend.adapter", model_name=model_name)
            detail_record = adapter.read(child_record)

            mapper = self._get_map_child_component(model_name)
            items = mapper.get_items(
                [detail_record], map_record, to_attr, options=self.options
            )
            # find if the sage id already exists in odoo
            external_id = [
                detail_record["CodigoEmpresa"],
                detail_record["CodigoConvenio"],
                detail_record["FechaRegistroCV"],
                detail_record["CodigoConceptoNom"],
            ]
            binding = adapter.binder_for().to_internal(external_id)
            if binding:
                children.extend([(1, binding.id, items[0][2])])
            else:
                children.extend(items)
        return children

    # def _map_child(self, map_record, from_attr, to_attr, model_name):
    #     """ Convert items of the record as defined by children """
    #     assert self._map_child_usage is not None, "_map_child_usage required"
    #     child_records = map_record.source[from_attr]
    #     mapper_child = self._get_map_child_component(model_name)
    #     items = mapper_child.get_items(child_records, map_record,
    #                                    to_attr, options=self.options)
    #     return items

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

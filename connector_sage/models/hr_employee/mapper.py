# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class HrEmployeeImportMapper(Component):
    _name = "sage.hr.employee.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.hr.employee"

    direct = [
        ("Email1", "work_email"),
        ("NumeroHijos", "children"),
        ("FechaNacimiento", "birthday"),
        ("CodigoEmpresa", "sage_codigo_empresa"),
        ("CodigoEmpleado", "sage_codigo_empleado"),
    ]

    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    @mapping
    def identification_id(self, record):
        parts = [part for part in (record["SiglaNacion"], record["Dni"]) if part]
        return {"identification_id": "".join(parts).strip().upper()}

    @mapping
    def names(self, record):
        parts = [
            part
            for part in (
                record["NombreEmpleado"],
                record["PrimerApellidoEmpleado"],
                record["SegundoApellidoEmpleado"],
            )
            if part
        ]
        return {"name": " ".join(parts)}

    # @mapping
    # def gender(self, record):
    #     mapping = {
    #         0: 'male',
    #         1: 'female',
    #     }
    #     Sexo
    #     return gender1
    #
    # @mapping
    # def marital(self, record):
    #     mapping = {
    #         0: 'male',
    #         1: 'female',
    #     }
    #     EstadoCivil
    #     return gender1

    @mapping
    def email2_notes(self, record):
        if record["Email1"] != record["Email2"]:
            return {"notes": record["Email2"]}

    @mapping
    def address_home_id(self, record):
        external_id = (record["CodigoEmpresa"], record["CodigoEmpleado"])

        binder = self.binder_for("sage.res.partner")
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
            "customer_id %s should have been imported in "
            "HrEmployeeImporter._import_dependencies" % external_id
        )
        return {"address_home_id": partner.id}

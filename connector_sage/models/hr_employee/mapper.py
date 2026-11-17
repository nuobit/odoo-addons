# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class HrEmployeeImportMapper(Component):
    _name = "sage.hr.employee.import.mapper"
    _inherit = "sage.import.mapper"
    _apply_on = "sage.hr.employee"

    direct = [
        # No ("Email1", "work_email"): Odoo writes the work email into the work
        # contact, which can be a partner found by its VAT
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
        nif_pattern = self.backend_record.employees_exclude_nif_pattern
        if nif_pattern:
            m = re.match(nif_pattern, record["Dni"])
            if m:
                return {"identification_id": record["Dni"]}
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

    def _work_contact(self, record):
        external_id = (record["CodigoEmpresa"], record["CodigoEmpleado"])

        binder = self.binder_for("sage.res.partner")
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
            f"customer_id {external_id} should have been imported in "
            "HrEmployeeImporter._import_dependencies"
        )
        return partner

    @only_create
    @mapping
    def work_contact_id(self, record):
        return {"work_contact_id": self._work_contact(record).id}

    @only_create
    @mapping
    def image_1920(self, record):
        # Odoo copies the avatar it generates for a new employee without an
        # image to the work contact (hr.employee.create). The work contact can
        # be a partner found by its VAT, which keeps its image, so the employee
        # gets one first: the contact's, or the avatar Odoo would generate,
        # under the same access check.
        work_contact = self._work_contact(record)
        if work_contact.image_1920:
            image = work_contact.image_1920
        elif self.env["ir.ui.view"].sudo(False).has_access("write"):
            image = (
                self.env["hr.employee"]
                .new({"name": self.names(record)["name"]})
                ._avatar_generate_svg()
            )
        else:
            image = False
        return {"image_1920": image}

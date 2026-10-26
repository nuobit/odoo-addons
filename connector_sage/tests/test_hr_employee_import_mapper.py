# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import TransactionComponentCase


class TestHrEmployeeImportMapper(TransactionComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env["sage.backend"].create(
            {
                "name": "Sage test",
                "company_id": cls.env.company.id,
                "server": "sage.example.com",
                "port": 1433,
                "database": "sage_test",
                "schema": "dbo",
                "username": "sage_test",
                "password": "sage_test",
                "sage_company_id": 1,
            }
        )
        cls.partner_binding = cls.env["sage.res.partner"].create(
            {
                "backend_id": cls.backend.id,
                "name": "Employee Test",
                "sage_codigo_empresa": 1,
                "sage_codigo_empleado": 7,
            }
        )
        cls.sage_employee = {
            "CodigoEmpresa": 1,
            "CodigoEmpleado": 7,
            "NombreEmpleado": "Employee",
            "PrimerApellidoEmpleado": "Test",
            "SegundoApellidoEmpleado": None,
            "SiglaNacion": "ES",
            "Dni": "00000000T",
            "Email1": "employee.test@example.com",
            "Email2": "employee.test@example.com",
            "NumeroHijos": 0,
            "FechaNacimiento": None,
        }

    def test_new_employee_work_contact_is_its_sage_partner(self):
        with self.backend.work_on("sage.hr.employee") as work:
            mapper = work.component(usage="import.mapper")
            values = mapper.map_record(self.sage_employee).values(for_create=True)
        self.assertEqual(values["work_contact_id"], self.partner_binding.odoo_id.id)
        self.assertNotIn("private_street", values)

    def test_employee_update_keeps_its_work_contact(self):
        with self.backend.work_on("sage.hr.employee") as work:
            mapper = work.component(usage="import.mapper")
            values = mapper.map_record(self.sage_employee).values()
        self.assertNotIn("work_contact_id", values)
        self.assertNotIn("private_street", values)

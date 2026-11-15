# Copyright NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from unittest import mock

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase, tagged

ADAPTER_READ = "odoo.addons.connector_sage.components.adapter.GenericAdapter.read"

SAGE_COMPANY = 1
CODE = 501

PERSON_A = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "SiglaNacion": "XX",
    "Dni": "TRIP0001A",
    "NombreEmpleado": "MARIA",
    "PrimerApellidoEmpleado": "GARCIA",
    "SegundoApellidoEmpleado": "PEREZ",
    "NumeroHijos": 0,
    "FechaNacimiento": False,
    "Email1": "maria@test.example.com",
    "Email2": "maria@test.example.com",
}

PERSON_B = {
    **PERSON_A,
    "Dni": "TRIP0002B",
    "NombreEmpleado": "JUAN",
    "PrimerApellidoEmpleado": "LOPEZ",
    "SegundoApellidoEmpleado": "RUIZ",
    "Email1": "juan@test.example.com",
    "Email2": "juan@test.example.com",
}


@tagged("post_install", "-at_install")
class TestEmployeeCodeReassignment(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env["res.company"].create({"name": "Sage Test Company"})
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test Account Payable",
                "code": "TESTPAY01",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
                "company_id": cls.company.id,
            }
        )
        cls.backend = cls.env["sage.backend"].create(
            {
                "name": "Test Sage Backend",
                "server": "localhost",
                "port": 1433,
                "database": "test",
                "schema": "dbo",
                "username": "test",
                "password": "test",
                "company_id": cls.company.id,
                "sage_company_id": SAGE_COMPANY,
                "import_employees_default_account_payable_id": cls.account_payable.id,
            }
        )

    def _import_record(self, binding_model, record):
        with mock.patch(ADAPTER_READ, return_value=dict(record)):
            self.env[binding_model].import_record(
                self.backend, (record["CodigoEmpresa"], record["CodigoEmpleado"])
            )
        return self.env[binding_model].search(
            [
                ("backend_id", "=", self.backend.id),
                ("sage_codigo_empresa", "=", record["CodigoEmpresa"]),
                ("sage_codigo_empleado", "=", record["CodigoEmpleado"]),
            ]
        )

    def test_first_import_sets_partner_vat(self):
        """The first import creates the partner with
        vat = SiglaNacion+Dni: the frozen identity every later sync
        validates against."""
        binding = self._import_record("sage.res.partner", PERSON_A)
        self.assertEqual(binding.odoo_id.vat, "XXTRIP0001A")
        self.assertEqual(binding.odoo_id.name, "MARIA GARCIA PEREZ")

    def test_same_person_reimport_passes(self):
        """A re-sync of the same person (e.g. renamed) must pass the
        guard and keep the partner untouched: partner data is
        @only_create."""
        binding = self._import_record("sage.res.partner", PERSON_A)
        renamed = dict(PERSON_A, PrimerApellidoEmpleado="GARCIA VIUDA")
        self._import_record("sage.res.partner", renamed)
        self.assertEqual(binding.odoo_id.vat, "XXTRIP0001A")
        self.assertEqual(binding.odoo_id.name, "MARIA GARCIA PEREZ")

    def test_reassigned_code_stops_import(self):
        """A code coming back with a different identity aborts before
        writing: neither the partner nor the binding may change."""
        binding = self._import_record("sage.res.partner", PERSON_A)
        with self.assertRaisesRegex(ValidationError, "reassigned"):
            self._import_record("sage.res.partner", PERSON_B)
        self.assertEqual(binding.odoo_id.name, "MARIA GARCIA PEREZ")
        self.assertEqual(binding.odoo_id.vat, "XXTRIP0001A")

    def test_partner_without_vat_skips_check(self):
        """Partners whose vat is empty (e.g. excluded by
        employees_exclude_nif_pattern) cannot be checked: the import
        proceeds and vat stays empty (@only_create never rewrites
        it)."""
        binding = self._import_record("sage.res.partner", PERSON_A)
        binding.odoo_id.vat = False
        self._import_record("sage.res.partner", PERSON_B)
        self.assertFalse(binding.odoo_id.vat)

    def test_employee_import_stops_before_updating_employee(self):
        """The employee import runs the partner import as a dependency
        (always=True), so the partner guard aborts the job before the
        employee is touched."""
        emp_binding = self._import_record("sage.hr.employee", PERSON_A)
        employee = emp_binding.odoo_id
        self.assertEqual(employee.name, "MARIA GARCIA PEREZ")
        self.assertEqual(employee.address_home_id.vat, "XXTRIP0001A")
        with self.assertRaisesRegex(ValidationError, "reassigned"):
            self._import_record("sage.hr.employee", PERSON_B)
        self.assertEqual(employee.name, "MARIA GARCIA PEREZ")
        self.assertEqual(employee.identification_id, "XXTRIP0001A")

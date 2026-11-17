# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

import pymssql

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase, tagged

ADAPTER_READ = "odoo.addons.connector_sage.components.adapter.GenericAdapter.read"

SAGE_COMPANY = 1
CODE = 601
VAT = "XXOWNER001A"

WORKER = {
    "CodigoEmpresa": SAGE_COMPANY,
    "CodigoEmpleado": CODE,
    "SiglaNacion": "XX",
    "Dni": "OWNER001A",
    "NombreEmpleado": "ANA",
    "PrimerApellidoEmpleado": "MARTIN",
    "SegundoApellidoEmpleado": "SOLER",
    "NumeroHijos": 0,
    "FechaNacimiento": False,
    "Email1": "ana@test.example.com",
    "Email2": "ana@test.example.com",
}


@tagged("post_install", "-at_install")
class TestVatOwnerLookup(SavepointCase):
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

    def test_company_with_contact_binds_company(self):
        """Odoo copies the company's VAT to its contact, but only the
        company owns it: the worker is bound to the company, which keeps
        its data, and no partner is created."""
        supplier_account = self.env["account.account"].create(
            {
                "name": "Supplier Account Payable",
                "code": "TESTPAY02",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
                "company_id": self.company.id,
            }
        )
        supplier = (
            self.env["res.partner"]
            .with_company(self.company)
            .create(
                {
                    "name": "SUPPLIER",
                    "is_company": True,
                    "vat": VAT,
                    "email": "supplier@test.example.com",
                    "company_id": self.company.id,
                    "property_account_payable_id": supplier_account.id,
                }
            )
        )
        contact = self.env["res.partner"].create(
            {
                "name": "SUPPLIER CONTACT",
                "parent_id": supplier.id,
                "company_id": self.company.id,
            }
        )
        self.assertEqual(contact.vat, VAT)
        partner_count = self.env["res.partner"].search_count([])
        employee = self._import_record("sage.hr.employee", WORKER)
        self.assertEqual(supplier.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(employee.address_home_id, supplier)
        self.assertEqual(supplier.name, "SUPPLIER")
        self.assertTrue(supplier.is_company)
        self.assertEqual(supplier.email, "supplier@test.example.com")
        self.assertFalse(supplier.ref)
        self.assertEqual(
            supplier.with_company(self.company).property_account_payable_id,
            supplier_account,
        )
        self.assertEqual(self.env["res.partner"].search_count([]), partner_count)

    def test_individual_with_vat_is_bound(self):
        """An individual who owns the VAT and has no contacts is bound."""
        person = self.env["res.partner"].create(
            {
                "name": "ANA MARTIN",
                "vat": VAT,
                "company_id": self.company.id,
            }
        )
        employee = self._import_record("sage.hr.employee", WORKER)
        self.assertEqual(person.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(employee.address_home_id, person)

    def test_vat_not_found_creates_partner(self):
        """Nobody has the worker's VAT: the import creates the partner."""
        employee = self._import_record("sage.hr.employee", WORKER)
        partner = employee.address_home_id
        self.assertEqual(partner.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(partner.name, "ANA MARTIN SOLER")
        self.assertEqual(partner.vat, VAT)

    def test_two_owners_stop_import(self):
        """Two companies own the VAT: the import cannot choose between
        them, and the error names both, so that they can be merged or the
        wrong VAT corrected. It leaves the VAT out, because the VAT is
        personal data."""
        supplier_1 = self.env["res.partner"].create(
            {
                "name": "SUPPLIER 1",
                "is_company": True,
                "vat": VAT,
                "company_id": self.company.id,
            }
        )
        supplier_2 = self.env["res.partner"].create(
            {
                "name": "SUPPLIER 2",
                "is_company": True,
                "vat": VAT,
                "company_id": self.company.id,
            }
        )
        with self.assertRaisesRegex(
            ValidationError,
            r"\(partner IDs: %d, %d\)" % (supplier_1.id, supplier_2.id),
        ) as error:
            self._import_record("sage.hr.employee", WORKER)
        self.assertNotIn(VAT, str(error.exception))
        self.assertFalse(
            self.env["sage.res.partner"].search([("sage_codigo_empleado", "=", CODE)])
        )
        self.assertFalse(
            self.env["sage.hr.employee"].search([("sage_codigo_empleado", "=", CODE)])
        )

    def test_archived_company_creates_partner(self):
        """The archived company is skipped, as archived partners are, and
        its active contact only carries a copy of the VAT: the import
        creates a new partner and the contact is not bound."""
        supplier = self.env["res.partner"].create(
            {
                "name": "SUPPLIER",
                "is_company": True,
                "vat": VAT,
                "company_id": self.company.id,
            }
        )
        contact = self.env["res.partner"].create(
            {
                "name": "SUPPLIER CONTACT",
                "parent_id": supplier.id,
                "company_id": self.company.id,
            }
        )
        supplier.action_archive()
        self.assertTrue(contact.active)
        self.assertEqual(contact.vat, VAT)
        employee = self._import_record("sage.hr.employee", WORKER)
        partner = employee.address_home_id
        self.assertEqual(partner.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(partner.name, "ANA MARTIN SOLER")
        self.assertFalse(contact.sage_bind_ids)

    def test_company_under_company_is_bound(self):
        """A company that hangs from another company is still its own
        commercial partner, so it owns its VAT: the worker is bound to it."""
        holding = self.env["res.partner"].create(
            {
                "name": "HOLDING",
                "is_company": True,
                "company_id": self.company.id,
            }
        )
        supplier = self.env["res.partner"].create(
            {
                "name": "SUPPLIER",
                "is_company": True,
                "parent_id": holding.id,
                "vat": VAT,
                "company_id": self.company.id,
            }
        )
        self.assertEqual(supplier.vat, VAT)
        employee = self._import_record("sage.hr.employee", WORKER)
        self.assertEqual(supplier.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(employee.address_home_id, supplier)

    def test_contact_with_own_vat_creates_partner(self):
        """A contact can be given a VAT of its own after it is created, but
        its company is its commercial partner, so the contact does not own
        that VAT: the import creates a new partner and binds neither."""
        supplier = self.env["res.partner"].create(
            {
                "name": "SUPPLIER",
                "is_company": True,
                "company_id": self.company.id,
            }
        )
        contact = self.env["res.partner"].create(
            {
                "name": "SUPPLIER CONTACT",
                "parent_id": supplier.id,
                "company_id": self.company.id,
            }
        )
        contact.vat = VAT
        self.assertFalse(supplier.vat)
        employee = self._import_record("sage.hr.employee", WORKER)
        partner = employee.address_home_id
        self.assertEqual(partner.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(partner.name, "ANA MARTIN SOLER")
        self.assertFalse(contact.sage_bind_ids)
        self.assertFalse(supplier.sage_bind_ids)

    def test_owner_in_another_company_is_not_seen(self):
        """The lookup runs as the cron user and only in the backend's
        company: a partner of another company of that user owns the VAT,
        but it is not seen, and the import creates a new partner."""
        other_company = self.env["res.company"].create({"name": "Other Company"})
        groups = (
            self.env.ref("base.group_user")
            | self.env.ref("base.group_partner_manager")
            | self.env.ref("hr.group_hr_user")
            | self.env.ref("connector.group_connector_manager")
        )
        cron_user = self.env["res.users"].create(
            {
                "name": "Sage Cron User",
                "login": "sage_cron_user",
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id, other_company.id])],
                "groups_id": [(6, 0, groups.ids)],
            }
        )
        supplier = self.env["res.partner"].create(
            {
                "name": "SUPPLIER",
                "is_company": True,
                "vat": VAT,
                "company_id": other_company.id,
            }
        )
        with mock.patch(ADAPTER_READ, return_value=dict(WORKER)):
            self.env["sage.hr.employee"].with_user(cron_user).import_record(
                self.backend.with_user(cron_user), (SAGE_COMPANY, CODE)
            )
        employee = self.env["sage.hr.employee"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("sage_codigo_empresa", "=", SAGE_COMPANY),
                ("sage_codigo_empleado", "=", CODE),
            ]
        )
        partner = employee.address_home_id
        self.assertEqual(partner.sage_bind_ids.sage_codigo_empleado, CODE)
        self.assertEqual(partner.name, "ANA MARTIN SOLER")
        self.assertFalse(supplier.sage_bind_ids)

    def test_sage_read_error_stops_import(self):
        """Sage cannot be read: the import stops with the database error,
        and nothing is created."""
        partner_count = self.env["res.partner"].search_count([])
        with mock.patch(
            ADAPTER_READ,
            side_effect=pymssql.OperationalError("Unable to connect to Sage"),
        ):
            with self.assertRaisesRegex(
                pymssql.OperationalError, "Unable to connect to Sage"
            ):
                self.env["sage.hr.employee"].import_record(
                    self.backend, (SAGE_COMPANY, CODE)
                )
        self.assertFalse(
            self.env["sage.hr.employee"].search([("sage_codigo_empleado", "=", CODE)])
        )
        self.assertEqual(self.env["res.partner"].search_count([]), partner_count)

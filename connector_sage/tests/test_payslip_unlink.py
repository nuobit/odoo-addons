# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPayslipUnlink(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Company"})
        cls.agreement = cls.env["payroll.sage.labour.agreement"].create(
            {
                "name": "Labour agreement",
                "code": 1,
                "registration_date_cv": "2026-01-01",
                "company_id": cls.company.id,
            }
        )
        cls.wage_type_line = cls.env[
            "payroll.sage.labour.agreement.wage.type.line"
        ].create(
            {
                "name": "Wage type",
                "short_name": "Wage type",
                "code": 1,
                "labour_agreement_id": cls.agreement.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Payroll",
                "code": "PAYRL",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.process = cls.env["payroll.sage.payslip.process"].create(
            {"name": "Payslip unlink process"}
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Employee", "company_id": cls.company.id}
        )
        cls.payslip = cls.env["payroll.sage.payslip"].create(
            {
                "name": "Payslip",
                "entry_date": "2026-01-31",
                "year": 2026,
                "month_from": 1,
                "month_to": 1,
                "labour_agreement_id": cls.agreement.id,
                "company_id": cls.company.id,
                "journal_id": cls.journal.id,
                "type": "transfer",
                "process_id": cls.process.id,
            }
        )
        cls.line = cls.env["payroll.sage.payslip.line"].create(
            {
                "payslip_id": cls.payslip.id,
                "wage_type_line_id": cls.wage_type_line.id,
                "employee_id": cls.employee.id,
                "amount": 1000,
            }
        )
        cls.check = cls.env["payroll.sage.payslip.check"].create(
            {
                "payslip_id": cls.payslip.id,
                "employee_id": cls.employee.id,
                "amount": 900,
            }
        )

    def test_payslip_unlink_removes_lines_checks_and_wage_types(self):
        wage_type = self.env["payroll.sage.payslip.wage.type"].create(
            {
                "payslip_id": self.payslip.id,
                "wage_type_line_id": self.wage_type_line.id,
                "amount": 1000,
            }
        )
        self.payslip.unlink()
        self.assertFalse(self.line.exists())
        self.assertFalse(self.check.exists())
        self.assertFalse(wage_type.exists())

    def test_payslip_unlink_removes_sage_bindings(self):
        backend = self.env["sage.backend"].create(
            {
                "name": "Sage",
                "server": "sage.example.com",
                "port": 1433,
                "database": "sage",
                "schema": "dbo",
                "username": "sage_test",
                "password": "sage_test",
                "company_id": self.company.id,
                "sage_company_id": 1,
            }
        )
        line_values = {
            "backend_id": backend.id,
            "odoo_id": self.line.id,
            "sage_codigo_empresa": 1,
            "sage_codigo_convenio": 1,
            "sage_fecha_registro_cv": "2026-01-01",
            "sage_ano": 2026,
            "sage_mesd": 1,
            "sage_tipo_proceso": "PROCESS",
            "sage_codigo_empleado": 1,
            "sage_codigo_concepto_nom": 1,
        }
        transfer_binding = self.env["sage.payroll.sage.payslip.line.transfer"].create(
            dict(line_values, sage_fecha_cobro="2026-01-31")
        )
        payroll_binding = self.env["sage.payroll.sage.payslip.line.payroll"].create(
            line_values
        )
        check_binding = self.env["sage.payroll.sage.payslip.check"].create(
            {
                "backend_id": backend.id,
                "odoo_id": self.check.id,
                "sage_codigo_empresa": 1,
                "sage_codigo_empleado": 1,
                "sage_ano": 2026,
                "sage_mesd": 1,
                "sage_tipo_proceso": "PROCESS",
                "sage_id_empleado": "EMPLOYEE",
                "sage_orden_nom": 1,
            }
        )
        self.payslip.unlink()
        self.assertFalse(transfer_binding.exists())
        self.assertFalse(payroll_binding.exists())
        self.assertFalse(check_binding.exists())

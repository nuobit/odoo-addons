# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPayslip(AccountTestInvoicingCommon):
    @classmethod
    def get_default_groups(cls):
        return super().get_default_groups() | cls.env.ref("payroll_sage.group_user")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.company_data["company"]
        cls.wages_account = cls.company_data["default_account_expense"]
        cls.wages_payable_account = cls.company_data["default_account_payable"]
        cls.work_contact = cls.env["res.partner"].create({"name": "Payroll Employee"})
        employee = (
            cls.env["hr.employee"]
            .sudo()
            .create(
                {
                    "name": "Payroll Employee",
                    "work_contact_id": cls.work_contact.id,
                    "company_id": company.id,
                }
            )
        )
        wages_tag = cls.env["payroll.sage.wage.tag"].create(
            {
                "sequence": 1,
                "type": "payroll",
                "account_id": cls.wages_account.id,
                "credit_debit": "debit",
                "company_id": company.id,
            }
        )
        wages_payable_tag = cls.env["payroll.sage.wage.tag"].create(
            {
                "sequence": 2,
                "type": "payroll",
                "account_id": cls.wages_payable_account.id,
                "credit_debit": "credit",
                "aggregate": True,
                "company_id": company.id,
            }
        )
        labour_agreement = cls.env["payroll.sage.labour.agreement"].create(
            {
                "name": "Labour Agreement",
                "code": 1,
                "registration_date_cv": "2026-01-01",
                "company_id": company.id,
            }
        )
        wage_type_line = cls.env["payroll.sage.labour.agreement.wage.type.line"].create(
            {
                "name": "Base Salary",
                "short_name": "Base",
                "code": 1,
                "positive": True,
                "total_historical_record": "accrural",
                "wage_tag_ids": [Command.set([wages_tag.id, wages_payable_tag.id])],
                "labour_agreement_id": labour_agreement.id,
            }
        )
        process = cls.env["payroll.sage.payslip.process"].create(
            {"name": "Monthly Payroll"}
        )
        cls.payslip = cls.env["payroll.sage.payslip"].create(
            {
                "name": "Payroll 10/2026",
                "entry_date": "2026-10-31",
                "year": 2026,
                "month_from": 10,
                "month_to": 10,
                "labour_agreement_id": labour_agreement.id,
                "company_id": company.id,
                "journal_id": cls.company_data["default_journal_misc"].id,
                "type": "payroll",
                "process_id": process.id,
                "payslip_line_ids": [
                    Command.create(
                        {
                            "name": "Base Salary",
                            "wage_type_line_id": wage_type_line.id,
                            "employee_id": employee.id,
                            "amount": 1000.0,
                        }
                    )
                ],
            }
        )

    def test_post_employee_partner(self):
        self.payslip.action_paysplip_post()
        self.assertRecordValues(
            self.payslip.move_id.line_ids,
            [
                {
                    "account_id": self.wages_account.id,
                    "partner_id": self.work_contact.id,
                    "debit": 1000.0,
                    "credit": 0.0,
                },
                {
                    "account_id": self.wages_payable_account.id,
                    "partner_id": False,
                    "debit": 0.0,
                    "credit": 1000.0,
                },
            ],
        )

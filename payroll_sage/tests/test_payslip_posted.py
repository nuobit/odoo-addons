# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase, tagged

POSTED = (
    r"Lines and checks of a posted payslip cannot be created, changed or "
    r"deleted \(Posted Transfer\)\."
)
POSTED_BOTH = (
    r"Lines and checks of a posted payslip cannot be created, changed or "
    r"deleted \(Posted Transfer, Repeated Transfer\)\."
)


@tagged("post_install", "-at_install")
class TestPayslipPosted(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env["res.company"].create({"name": "Payroll Test Company"})
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test Salaries",
                "code": "TESTSAL01",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "company_id": cls.company.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Payroll Journal",
                "code": "TPAY",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        cls.process = cls.env["payroll.sage.payslip.process"].create(
            {"name": "TEST-POSTED"}
        )
        cls.agreement = cls.env["payroll.sage.labour.agreement"].create(
            {
                "name": "TEST AGREEMENT",
                "code": 91,
                "registration_date_cv": date(2020, 1, 1),
                "company_id": cls.company.id,
            }
        )
        debit_tag = cls.env["payroll.sage.wage.tag"].create(
            {
                "type": "transfer",
                "account_id": cls.account.id,
                "credit_debit": "debit",
                "aggregate": True,
                "company_id": cls.company.id,
            }
        )
        credit_tag = cls.env["payroll.sage.wage.tag"].create(
            {
                "type": "transfer",
                "account_id": cls.account.id,
                "credit_debit": "credit",
                "aggregate": True,
                "company_id": cls.company.id,
            }
        )
        cls.wage_type_line = cls.env[
            "payroll.sage.labour.agreement.wage.type.line"
        ].create(
            {
                "labour_agreement_id": cls.agreement.id,
                "name": "SALARIO BASE",
                "short_name": "SALARIO",
                "code": 901,
                "positive": True,
                "total_historical_record": "accrural",
                "wage_tag_ids": [(6, 0, [debit_tag.id, credit_tag.id])],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Joan Puig", "company_id": cls.company.id}
        )

    def _create_payslip(self, name):
        """A validated transfer of January with one line and one check."""
        payslip = self.env["payroll.sage.payslip"].create(
            {
                "name": name,
                "entry_date": date(2026, 2, 1),
                "year": 2026,
                "month_from": 1,
                "month_to": 1,
                "labour_agreement_id": self.agreement.id,
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "type": "transfer",
                "process_id": self.process.id,
                "payslip_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "SALARIO BASE",
                            "wage_type_line_id": self.wage_type_line.id,
                            "employee_id": self.employee.id,
                            "amount": 1000.0,
                        },
                    )
                ],
                "payslip_check_ids": [
                    (0, 0, {"employee_id": self.employee.id, "amount": 900.0})
                ],
            }
        )
        payslip.action_paysplip_validate()
        return payslip

    def test_post_is_allowed(self):
        """Posting writes the payslip and not its lines or checks, so the lock
        does not stop it."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        self.assertEqual(payslip.state, "posted")
        self.assertEqual(payslip.move_id.state, "posted")

    def test_line_cannot_be_added_to_posted_payslip(self):
        """A line created in a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            self.env["payroll.sage.payslip.line"].create(
                {
                    "name": "PLUS",
                    "wage_type_line_id": self.wage_type_line.id,
                    "employee_id": self.employee.id,
                    "amount": 50.0,
                    "payslip_id": payslip.id,
                }
            )
        self.assertEqual(payslip.payslip_line_ids.mapped("amount"), [1000.0])

    def test_line_of_posted_payslip_cannot_be_changed(self):
        """Changing a line of a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            payslip.payslip_line_ids.amount = 1001.0
        self.assertEqual(payslip.payslip_line_ids.mapped("amount"), [1000.0])

    def test_line_of_posted_payslip_cannot_be_deleted(self):
        """Deleting a line of a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        line = payslip.payslip_line_ids
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            line.unlink()
        self.assertTrue(line.exists())

    def test_line_cannot_be_moved_into_posted_payslip(self):
        """A line of a validated payslip cannot be moved to a posted one."""
        posted = self._create_payslip("Posted Transfer")
        posted.action_paysplip_post()
        validated = self._create_payslip("Validated Transfer")
        line = validated.payslip_line_ids
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            line.payslip_id = posted
        self.assertEqual(line.payslip_id, validated)

    def test_check_cannot_be_added_to_posted_payslip(self):
        """A check created in a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            self.env["payroll.sage.payslip.check"].create(
                {
                    "employee_id": self.employee.id,
                    "amount": 40.0,
                    "payslip_id": payslip.id,
                }
            )
        self.assertEqual(payslip.payslip_check_ids.mapped("amount"), [900.0])

    def test_check_of_posted_payslip_cannot_be_changed(self):
        """Changing a check of a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            payslip.payslip_check_ids.amount = 901.0
        self.assertEqual(payslip.payslip_check_ids.mapped("amount"), [900.0])

    def test_check_of_posted_payslip_cannot_be_deleted(self):
        """Deleting a check of a posted payslip is refused."""
        payslip = self._create_payslip("Posted Transfer")
        payslip.action_paysplip_post()
        check = payslip.payslip_check_ids
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            check.unlink()
        self.assertTrue(check.exists())

    def test_check_cannot_be_moved_into_posted_payslip(self):
        """A check of a validated payslip cannot be moved to a posted one."""
        posted = self._create_payslip("Posted Transfer")
        posted.action_paysplip_post()
        validated = self._create_payslip("Validated Transfer")
        check = validated.payslip_check_ids
        with self.assertRaisesRegex(UserError, POSTED), self.cr.savepoint():
            check.payslip_id = posted
        self.assertEqual(check.payslip_id, validated)

    def test_lines_of_several_posted_payslips(self):
        """Deleting lines of two posted payslips at once names both of them."""
        january = self._create_payslip("Posted Transfer")
        january.action_paysplip_post()
        repeated = self._create_payslip("Repeated Transfer")
        repeated.action_paysplip_post()
        lines = january.payslip_line_ids + repeated.payslip_line_ids
        with self.assertRaisesRegex(UserError, POSTED_BOTH), self.cr.savepoint():
            lines.unlink()
        self.assertTrue(lines.exists())

    def test_lines_of_validated_payslip_can_change(self):
        """The lock is only for posted payslips: the lines of a validated
        payslip can still be created, changed and deleted."""
        payslip = self._create_payslip("Validated Transfer")
        line = payslip.payslip_line_ids
        line.amount = 1001.0
        self.env["payroll.sage.payslip.line"].create(
            {
                "name": "PLUS",
                "wage_type_line_id": self.wage_type_line.id,
                "employee_id": self.employee.id,
                "amount": 50.0,
                "payslip_id": payslip.id,
            }
        )
        self.assertEqual(payslip.payslip_line_ids.mapped("amount"), [1001.0, 50.0])
        line.unlink()
        self.assertEqual(payslip.payslip_line_ids.mapped("amount"), [50.0])

    def test_checks_of_validated_payslip_can_change(self):
        """The lock is only for posted payslips: the checks of a validated
        payslip can still be created, changed and deleted."""
        payslip = self._create_payslip("Validated Transfer")
        check = payslip.payslip_check_ids
        check.amount = 901.0
        self.env["payroll.sage.payslip.check"].create(
            {
                "employee_id": self.employee.id,
                "amount": 40.0,
                "payslip_id": payslip.id,
            }
        )
        self.assertEqual(payslip.payslip_check_ids.mapped("amount"), [901.0, 40.0])
        check.unlink()
        self.assertEqual(payslip.payslip_check_ids.mapped("amount"), [40.0])

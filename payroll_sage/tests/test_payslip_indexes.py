# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import PayslipIndexCase


@tagged("post_install", "-at_install")
class TestPayslipIndexes(PayslipIndexCase):
    def test_update_indexes_payslip_line_payslip_id(self):
        self._drop_indexes_led_by("payroll.sage.payslip.line", "payslip_id")
        self._update_indexes("payroll.sage.payslip.line")
        self.assertEqual(
            len(self._indexes_led_by("payroll.sage.payslip.line", "payslip_id")), 1
        )

    def test_update_indexes_payslip_check_payslip_id(self):
        self._drop_indexes_led_by("payroll.sage.payslip.check", "payslip_id")
        self._update_indexes("payroll.sage.payslip.check")
        self.assertEqual(
            len(self._indexes_led_by("payroll.sage.payslip.check", "payslip_id")), 1
        )

    def test_update_indexes_payslip_wage_type_payslip_id(self):
        self._drop_indexes_led_by("payroll.sage.payslip.wage.type", "payslip_id")
        self._update_indexes("payroll.sage.payslip.wage.type")
        self.assertEqual(
            len(self._indexes_led_by("payroll.sage.payslip.wage.type", "payslip_id")), 1
        )

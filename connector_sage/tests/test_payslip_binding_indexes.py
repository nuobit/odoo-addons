# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.payroll_sage.tests.common import PayslipIndexCase


@tagged("post_install", "-at_install")
class TestPayslipBindingIndexes(PayslipIndexCase):
    def test_update_indexes_payslip_line_transfer_binding_odoo_id(self):
        self._drop_indexes_led_by("sage.payroll.sage.payslip.line.transfer", "odoo_id")
        self._update_indexes("sage.payroll.sage.payslip.line.transfer")
        self.assertEqual(
            len(
                self._indexes_led_by(
                    "sage.payroll.sage.payslip.line.transfer", "odoo_id"
                )
            ),
            1,
        )

    def test_update_indexes_payslip_line_payroll_binding_odoo_id(self):
        self._drop_indexes_led_by("sage.payroll.sage.payslip.line.payroll", "odoo_id")
        self._update_indexes("sage.payroll.sage.payslip.line.payroll")
        self.assertEqual(
            len(
                self._indexes_led_by(
                    "sage.payroll.sage.payslip.line.payroll", "odoo_id"
                )
            ),
            1,
        )

    def test_update_indexes_payslip_check_binding_odoo_id(self):
        self._drop_indexes_led_by("sage.payroll.sage.payslip.check", "odoo_id")
        self._update_indexes("sage.payroll.sage.payslip.check")
        self.assertEqual(
            len(self._indexes_led_by("sage.payroll.sage.payslip.check", "odoo_id")), 1
        )

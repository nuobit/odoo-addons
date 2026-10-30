# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPayslipIndexes(common.SavepointCase):
    def _leading_index_columns(self, table):
        self.env.cr.execute(
            """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a
                ON a.attrelid = i.indrelid AND a.attnum = i.indkey[0]
            WHERE i.indrelid = %s::regclass
            """,
            (table,),
        )
        return [row[0] for row in self.env.cr.fetchall()]

    def test_payslip_line_payslip_id_indexed(self):
        self.assertIn(
            "payslip_id", self._leading_index_columns("payroll_sage_payslip_line")
        )

    def test_payslip_check_payslip_id_indexed(self):
        self.assertIn(
            "payslip_id", self._leading_index_columns("payroll_sage_payslip_check")
        )

    def test_payslip_wage_type_payslip_id_indexed(self):
        self.assertIn(
            "payslip_id",
            self._leading_index_columns("payroll_sage_payslip_wage_type"),
        )

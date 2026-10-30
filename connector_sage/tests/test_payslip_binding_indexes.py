# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestPayslipBindingIndexes(common.SavepointCase):
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

    def test_payslip_line_transfer_binding_odoo_id_indexed(self):
        self.assertIn(
            "odoo_id",
            self._leading_index_columns("sage_payroll_sage_payslip_line_transfer"),
        )

    def test_payslip_line_payroll_binding_odoo_id_indexed(self):
        self.assertIn(
            "odoo_id",
            self._leading_index_columns("sage_payroll_sage_payslip_line_payroll"),
        )

    def test_payslip_check_binding_odoo_id_indexed(self):
        self.assertIn(
            "odoo_id", self._leading_index_columns("sage_payroll_sage_payslip_check")
        )

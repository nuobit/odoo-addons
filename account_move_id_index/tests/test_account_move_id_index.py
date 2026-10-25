# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase
from odoo.tools.sql import drop_index, index_exists

from ..hooks import uninstall_hook


class TestAccountMoveIdIndex(TransactionCase):
    def test_payment_move_id_index(self):
        # delete the index and check that the index check Odoo runs on every
        # install and update of the module creates it again
        drop_index(self.env.cr, "account_payment_move_id_index", "account_payment")
        self.registry.check_indexes(self.env.cr, ["account.payment"])
        self.assertTrue(index_exists(self.env.cr, "account_payment_move_id_index"))

    def test_statement_line_move_id_index(self):
        drop_index(
            self.env.cr,
            "account_bank_statement_line_move_id_index",
            "account_bank_statement_line",
        )
        self.registry.check_indexes(self.env.cr, ["account.bank.statement.line"])
        self.assertTrue(
            index_exists(self.env.cr, "account_bank_statement_line_move_id_index")
        )

    def test_uninstall_hook(self):
        # the hook Odoo runs when the module is uninstalled drops both indexes
        uninstall_hook(self.env.cr, self.registry)
        self.assertFalse(index_exists(self.env.cr, "account_payment_move_id_index"))
        self.assertFalse(
            index_exists(self.env.cr, "account_bank_statement_line_move_id_index")
        )

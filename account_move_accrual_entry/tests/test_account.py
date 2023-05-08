# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from . import common

_logger = logging.getLogger(__name__)


class TestInvoice(common.CommonAccountMultiVat):
    # TEST CREATE ACCOUNT.MOVE
    def test_create_account_move(self):
        def create_acrrual_invoice(self):
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_7000.id,
                            },
                        )
                    ],
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_7000, self.accrual_account_id),
            )

        create_acrrual_invoice(self)

    # TEST WRITE ACCOUNT.MOVE
    def test_write_account_move(self):
        def write_accrual_date_in_invoice(self):
            #
            # Create invoice without accrual date
            # Write accrual date in invoice
            #
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_7000.id,
                            },
                        )
                    ],
                }
            )
            invoice.write(
                {
                    "accrual_date": self.date,
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_7000, self.accrual_account_id),
            )

        write_accrual_date_in_invoice(self)

        def accrual_invoice_to_normal_invoice(self):
            # CREATE & WRITE (ACCOUNT.MOVE)
            #
            # Create invoice with accrual date
            # Write False in accrual date
            #
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_7000.id,
                            },
                        )
                    ],
                }
            )
            invoice.write(
                {
                    "accrual_date": False,
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_empty, self.account_7000),
            )

        accrual_invoice_to_normal_invoice(self)

        def accrual_invoice_to_normal_modifying_accrual_account(self):
            # CREATE & WRITE (ACCOUNT.MOVE)
            #
            # Create invoice with accrual date
            # Write False in accrual date & modify accrual account
            #
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_7000.id,
                            },
                        )
                    ],
                }
            )
            invoice.write(
                {
                    "accrual_date": False,
                    "invoice_line_ids": [
                        (
                            1,
                            invoice.invoice_line_ids[0].id,
                            {
                                "accrual_account_id": self.account_100.id,
                            },
                        )
                    ],
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_empty, self.account_100),
            )

        accrual_invoice_to_normal_modifying_accrual_account(self)

    # TEST CREATE ACCOUNT.MOVE.LINE
    def test_create_account_move_line(self):
        def create_1_new_invoice_line(self):
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                    "move_type": "out_invoice",
                }
            )
            self.env["account.move.line"].create(
                {
                    "move_id": invoice.id,
                    "account_id": self.account_7000.id,
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_7000, self.accrual_account_id),
            )

        create_1_new_invoice_line(self)

        def create_2_new_invoice_line(self):
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                }
            )
            self.env["account.move.line"].create(
                [
                    {
                        "move_id": invoice.id,
                        "account_id": self.account_7000.id,
                    },
                    {
                        "move_id": invoice.id,
                        "account_id": self.account_100.id,
                    },
                ]
            )

            line = invoice.invoice_line_ids[0]
            line1 = invoice.invoice_line_ids[1]
            self.assertTupleEqual(
                (
                    line.accrual_account_id,
                    line.account_id,
                    line1.accrual_account_id,
                    line1.account_id,
                ),
                (
                    self.account_7000,
                    self.accrual_account_id,
                    self.account_100,
                    self.accrual_account_id,
                ),
            )

        create_2_new_invoice_line(self)

        def create_2_separate_new_invoice_line(self):
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                }
            )
            self.env["account.move.line"].create(
                {
                    "move_id": invoice.id,
                    "account_id": self.account_7000.id,
                }
            )
            self.env["account.move.line"].create(
                {
                    "move_id": invoice.id,
                    "account_id": self.account_100.id,
                }
            )

            line = invoice.invoice_line_ids[0]
            line1 = invoice.invoice_line_ids[1]
            self.assertTupleEqual(
                (
                    line.accrual_account_id,
                    line.account_id,
                    line1.accrual_account_id,
                    line1.account_id,
                ),
                (
                    self.account_7000,
                    self.accrual_account_id,
                    self.account_100,
                    self.accrual_account_id,
                ),
            )

        create_2_separate_new_invoice_line(self)

    # TEST WRITE ACCOUNT.MOVE.LINE
    def test_write_account_move_line(self):
        def write_accrual_account_invoice(self):
            #
            # Create invoice with accrual date
            # Write accrual account in invoice line
            #
            invoice = self.env["account.move"].create(
                {
                    "journal_id": self.journal.id,
                    "accrual_date": self.date,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": self.account_7000.id,
                            },
                        )
                    ],
                }
            )
            invoice.invoice_line_ids.write(
                {
                    "move_id": invoice.id,
                    "accrual_account_id": self.account_100.id,
                }
            )

            line = invoice.invoice_line_ids[0]
            self.assertTupleEqual(
                (line.accrual_account_id, line.account_id),
                (self.account_100, self.accrual_account_id),
            )

        write_accrual_account_invoice(self)

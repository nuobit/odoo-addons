# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import calendar
import datetime
import logging

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestAccountInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ARRANGE
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "vat": "ESA12345674",
                "facturae": True,
                "is_company": True,
                "country_id": cls.env.ref("base.es").id,
                "state_id": cls.env.ref("base.state_es_b").id,
            }
        )

    def test_01(self):
        # ACT
        self.partner.facturae_auto_dates = True
        date_invoice = datetime.date(2021, 4, 1)
        invoice = (
            self.env["account.move"]
            .with_context(move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner.id,
                    "invoice_date": date_invoice,
                    "move_type": "out_invoice",
                }
            )
        )
        # force partner onchange to populate 'factuare' field
        invoice_form = Form(invoice)
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = date_invoice
        invoice = invoice_form.save()

        # ASSERT
        _, month_days = calendar.monthrange(date_invoice.year, date_invoice.month)
        expected_values = [
            datetime.date(date_invoice.year, date_invoice.month, 1),
            datetime.date(date_invoice.year, date_invoice.month, month_days),
        ]
        self.assertEqual(
            [x for x in [invoice.facturae_start_date, invoice.facturae_end_date]],
            expected_values,
            "The FacturaE start and end dates does not match to the invoice date",
        )

    def test_02(self):
        # ARRANGE
        self.partner.facturae_auto_dates = True
        date_invoice = datetime.date(2021, 4, 13)
        invoice = (
            self.env["account.move"]
            .with_context(move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner.id,
                    "invoice_date": date_invoice,
                    "move_type": "out_invoice",
                }
            )
        )
        # force partner onchange to populate 'factuare' field
        invoice_form = Form(invoice)
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = date_invoice
        invoice = invoice_form.save()

        # ACT
        date_invoice2 = datetime.date(2021, 2, 13)

        invoice_form = Form(invoice)
        invoice_form.invoice_date = date_invoice2
        invoice = invoice_form.save()

        # ASSERT
        _, month_days = calendar.monthrange(date_invoice2.year, date_invoice2.month)
        expected_values = [
            datetime.date(date_invoice2.year, date_invoice2.month, 1),
            datetime.date(date_invoice2.year, date_invoice2.month, month_days),
        ]
        self.assertEqual(
            [x for x in [invoice.facturae_start_date, invoice.facturae_end_date]],
            expected_values,
            "The FacturaE start and end dates does not match to the invoice date",
        )

    def test_03(self):
        # ARRANGE
        self.partner.facturae_auto_dates = True
        date_invoice = datetime.date(2021, 4, 13)
        invoice = (
            self.env["account.move"]
            .with_context(move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner.id,
                    "invoice_date": date_invoice,
                    "move_type": "out_invoice",
                }
            )
        )
        # force partner onchange to populate 'factuare' field
        invoice_form = Form(invoice)
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = False
        invoice = invoice_form.save()

        # ASSERT
        self.assertEqual(
            [x for x in [invoice.facturae_start_date, invoice.facturae_end_date]],
            [False, False],
            "The FacturaE start and end dates does not match to the invoice date",
        )

    def test_04(self):
        # ARRANGE
        self.partner.facturae_auto_dates = True
        date_invoice = datetime.date(2021, 4, 13)
        invoice = (
            self.env["account.move"]
            .with_context(move_type="out_invoice")
            .create(
                {
                    "partner_id": self.partner.id,
                    "invoice_date": fields.Date.to_string(date_invoice),
                    "move_type": "out_invoice",
                }
            )
        )
        # force partner onchange to populate 'facturae' field

        invoice_form = Form(invoice)
        invoice.partner_id = self.partner
        invoice_form.facturae_start_date = False
        invoice_form.facturae_end_date = False
        invoice = invoice_form.save()

        # ASSERT
        self.assertEqual(
            [x for x in [invoice.facturae_start_date, invoice.facturae_end_date]],
            [False, False],
            "The FacturaE start and end dates does not match to the invoice date",
        )

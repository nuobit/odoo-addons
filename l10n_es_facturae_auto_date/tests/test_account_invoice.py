# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import calendar
import datetime
import logging

from odoo import fields
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestAccountInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ARRANGE
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'vat': 'ESA12345674',
            'facturae': True,
            'is_company': True,
            'customer': True,
            'country_id': cls.env.ref('base.es').id,
            'state_id': cls.env.ref('base.state_es_b').id,
        })

    def test_01(self):
        # ACT
        date_invoice = datetime.date(2021, 4, 1)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.to_string(date_invoice),
        })
        # force partner onchange to populate 'factuare' field
        invoice._onchange_partner_id()

        # ASSERT
        _, month_days = calendar.monthrange(date_invoice.year, date_invoice.month)
        expected_values = [
            datetime.date(date_invoice.year, date_invoice.month, 1),
            datetime.date(date_invoice.year, date_invoice.month, month_days)
        ]
        self.assertEqual(
            [fields.Date.from_string(x) for x in
             [invoice.facturae_start_date, invoice.facturae_end_date]],
            expected_values,
            'The FacturaE start and end dates does not match to the invoice date')

    def test_02(self):
        # ARRANGE
        date_invoice = datetime.date(2021, 4, 13)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.to_string(date_invoice),
        })
        # force partner onchange to populate 'factuare' field
        invoice._onchange_partner_id()

        # ACT
        date_invoice2 = datetime.date(2021, 2, 13)
        invoice.date_invoice = fields.Date.to_string(date_invoice2)

        # ASSERT
        _, month_days = calendar.monthrange(date_invoice2.year, date_invoice2.month)
        expected_values = [
            datetime.date(date_invoice2.year, date_invoice2.month, 1),
            datetime.date(date_invoice2.year, date_invoice2.month, month_days)
        ]
        self.assertEqual(
            [fields.Date.from_string(x) for x in
             [invoice.facturae_start_date, invoice.facturae_end_date]],
            expected_values,
            'The FacturaE start and end dates does not match to the invoice date')

    def test_03(self):
        # ARRANGE
        date_invoice = datetime.date(2021, 4, 13)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.to_string(date_invoice),
        })
        # force partner onchange to populate 'factuare' field
        invoice._onchange_partner_id()

        # ACT
        invoice.date_invoice = False

        # ASSERT
        self.assertEqual(
            [fields.Date.from_string(x) for x in
             [invoice.facturae_start_date, invoice.facturae_end_date]],
            [None, None],
            'The FacturaE start and end dates does not match to the invoice date')

    def test_04(self):
        # ARRANGE
        date_invoice = datetime.date(2021, 4, 13)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.to_string(date_invoice),
        })
        # force partner onchange to populate 'factuare' field
        invoice._onchange_partner_id()

        # ACT
        invoice.write({
            'facturae_start_date': False,
            'facturae_end_date': False
        })

        # ASSERT
        self.assertEqual(
            [fields.Date.from_string(x) for x in
             [invoice.facturae_start_date, invoice.facturae_end_date]],
            [None, None],
            'The FacturaE start and end dates does not match to the invoice date')

    def test_05(self):
        # ARRANGE
        date_invoice = datetime.date(2021, 4, 13)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.to_string(date_invoice),
        })
        # force partner onchange to populate 'factuare' field
        invoice._onchange_partner_id()

        # ACT
        invoice.write({
            'facturae_start_date': False,
            'facturae_end_date': False
        })
        invoice.name = 'Test Reference'

        # ASSERT
        _, month_days = calendar.monthrange(date_invoice.year, date_invoice.month)
        expected_values = [
            datetime.date(date_invoice.year, date_invoice.month, 1),
            datetime.date(date_invoice.year, date_invoice.month, month_days)
        ]
        self.assertEqual(
            [fields.Date.from_string(x) for x in
             [invoice.facturae_start_date, invoice.facturae_end_date]],
            expected_values,
            'The FacturaE start and end dates does not match to the invoice date')

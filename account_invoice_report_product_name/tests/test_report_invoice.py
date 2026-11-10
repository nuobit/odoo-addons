# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReportInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.product = cls.env["product.product"].create(
            {"name": "Rose bouquet", "default_code": "BQ01"}
        )
        cls.invoice = cls.init_invoice("out_invoice", products=cls.product, post=True)

    def _render_description_column(self):
        content = html.document_fromstring(
            self.env["ir.actions.report"]._render_qweb_html(
                "account.account_invoices", self.invoice.ids
            )[0]
        )
        headers = [
            header.text_content().strip()
            for header in content.xpath("//th[@name='th_description']")
        ]
        cells = [
            cell.text_content().strip()
            for cell in content.xpath("//td[@name='account_invoice_line_name']")
        ]
        return headers, cells

    def test_invoice_product_column(self):
        headers, cells = self._render_description_column()
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_standard_column_without_view(self):
        # Without the view of this module the invoice prints Odoo's own column
        self.env.ref(
            "account_invoice_report_product_name.report_invoice_document"
        ).active = False
        headers, cells = self._render_description_column()
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

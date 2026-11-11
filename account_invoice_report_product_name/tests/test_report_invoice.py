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

    def _render_description_column(self, invoice):
        content = html.document_fromstring(
            self.env["ir.actions.report"]._render_qweb_html(
                "account.account_invoices", invoice.ids
            )[0]
        )
        headers = [
            " ".join(header.text_content().split())
            for header in content.xpath("//th[@name='th_description']")
        ]
        cells = [
            " ".join(cell.text_content().split())
            for cell in content.xpath("//td[@name='account_invoice_line_name']")
        ]
        return headers, cells

    def test_invoice_product_column(self):
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_standard_column_without_view(self):
        # Without the view of this module the invoice prints Odoo's own column
        self.env.ref(
            "account_invoice_report_product_name.report_invoice_document"
        ).active = False
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_invoice_line_without_product_prints_its_label(self):
        # The amount adds a line without a product, labelled "test line"
        invoice = self.init_invoice(
            "out_invoice", products=self.product, amounts=[10.0], post=True
        )
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet", "test line"])

    def test_invoice_product_column_keeps_what_another_module_adds(self):
        # A view of another module adds a text inside the description cell, as
        # pos_sale does with the products of a point of sale down payment
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.description_cell",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": "<data><xpath"
                " expr=\"//td[@name='account_invoice_line_name']\""
                ' position="inside"><span> and its extra text</span></xpath></data>',
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet and its extra text"])

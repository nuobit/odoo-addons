# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReportInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, lang="en_US"))
        cls.partner_a.lang = "en_US"
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

    def _load_language(self, lang):
        self.env["res.lang"]._activate_lang(lang)
        self.env["ir.module.module"]._load_module_terms(
            ["account_invoice_report_product_name"], [lang]
        )

    def test_invoice_product_column(self):
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_product_column_spanish_customer(self):
        self._load_language("es_ES")
        self.product.with_context(lang="es_ES").name = "Ramo de rosas"
        self.partner_a.lang = "es_ES"
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Producto"])
        self.assertEqual(cells, ["Ramo de rosas"])

    def test_invoice_product_column_catalan_customer(self):
        self._load_language("ca_ES")
        self.product.with_context(lang="ca_ES").name = "Ram de roses"
        self.partner_a.lang = "ca_ES"
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Producte"])
        self.assertEqual(cells, ["Ram de roses"])

    def test_invoice_standard_column_without_view(self):
        # Without the view of this module the invoice prints Odoo's own column
        self.env.ref(
            "account_invoice_report_product_name.report_invoice_document"
        ).active = False
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_invoice_product_line_without_label_prints_its_product(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.invoice_line_ids.name = False
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_line_without_product_prints_its_label(self):
        invoice = self.init_invoice(
            "out_invoice", products=self.product, amounts=[10.0]
        )
        invoice.invoice_line_ids.filtered(
            lambda line: not line.product_id
        ).name = "Delivery"
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet", "Delivery"])

    def test_invoice_line_without_product_or_label_prints_nothing(self):
        invoice = self.init_invoice(
            "out_invoice", products=self.product, amounts=[10.0]
        )
        invoice.invoice_line_ids.filtered(lambda line: not line.product_id).name = False
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet", ""])

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

    def test_invoice_cell_without_its_label_span_is_refused(self):
        # A view that replaces the label's span leaves this module's view
        # without its anchor, and Odoo refuses it instead of printing it wrong
        with self.assertRaises(ValidationError):
            self.env["ir.ui.view"].create(
                {
                    "name": "test.report_invoice_document.label_span",
                    "type": "qweb",
                    "inherit_id": self.env.ref("account.report_invoice_document").id,
                    "arch": "<data><xpath"
                    " expr=\"//td[@name='account_invoice_line_name']/span\""
                    ' position="replace"><span>Another text</span></xpath></data>',
                }
            )

# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import html

from odoo import Command
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

    def _render_invoice(self, invoice):
        return html.document_fromstring(
            self.env["ir.actions.report"]._render_qweb_html(
                "account.account_invoices", invoice.ids
            )[0]
        )

    def _render_description_column(self, invoice):
        content = self._render_invoice(invoice)
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

    def test_credit_note_product_column(self):
        credit_note = self.init_invoice("out_refund", products=self.product, post=True)
        headers, cells = self._render_description_column(credit_note)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_receipt_product_column(self):
        receipt = self.init_invoice("out_receipt", products=self.product, post=True)
        headers, cells = self._render_description_column(receipt)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_vendor_bill_standard_column(self):
        bill = self.init_invoice("in_invoice", products=self.product, post=True)
        headers, cells = self._render_description_column(bill)
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_vendor_credit_note_standard_column(self):
        refund = self.init_invoice("in_refund", products=self.product, post=True)
        headers, cells = self._render_description_column(refund)
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_purchase_receipt_standard_column(self):
        receipt = self.init_invoice("in_receipt", products=self.product, post=True)
        headers, cells = self._render_description_column(receipt)
        self.assertEqual(headers, ["Description"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_invoice_and_vendor_bill_printed_together(self):
        # Each document of a print decides its own column: a vendor bill printed
        # after a customer invoice keeps Odoo's column
        bill = self.init_invoice("in_invoice", products=self.product, post=True)
        headers, cells = self._render_description_column(self.invoice + bill)
        self.assertEqual(headers, ["Product", "Description"])
        self.assertEqual(cells, ["Rose bouquet", "[BQ01] Rose bouquet"])

    def test_invoice_product_header_keeps_what_another_module_adds(self):
        # A view of another module adds a text inside the header of the column
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.description_header",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath expr="//th[@name='th_description']" position="inside">
                            <span> (and its extra text)</span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product (and its extra text)"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_header_span_keeps_what_a_later_view_puts_on_it(self):
        # A view applied after this module's that names the header's span keeps
        # its name, so that a view applied after it can still anchor on it
        report = self.env.ref("account.report_invoice_document")
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.header_span_name",
                "type": "qweb",
                "priority": 98,
                "inherit_id": report.id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="attributes"
                        >
                            <attribute name="name">description_label</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.after_header_span_name",
                "type": "qweb",
                "priority": 100,
                "inherit_id": report.id,
                "arch": """
                    <data>
                        <xpath
                            expr="//span[@name='description_label']"
                            position="after"
                        >
                            <span> (extra)</span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product (extra)"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_later_span_ahead_of_the_header_span_keeps_its_text(self):
        # A view applied after this module's that puts a span ahead of the
        # header's span: this module has changed Odoo's span already, so the new
        # span keeps its text and "Product" follows it. The view has priority 1,
        # as this module's has, and is applied after it because views of one
        # priority apply in the order they were created
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.before_header_span",
                "type": "qweb",
                "priority": 1,
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="before"
                        >
                            <span>(extra) </span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["(extra) Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_earlier_span_ahead_of_the_header_span_prints_product(self):
        # A view applied before this module's, with priority 0, that puts a span
        # ahead of the header's span: the new span is then the header's first,
        # so it prints "Product" and Odoo's span keeps its own text, as the
        # roadmap says
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.earlier_header_span",
                "type": "qweb",
                "priority": 0,
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="before"
                        >
                            <span>(extra) </span>
                        </xpath>
                    </data>
                """,
            }
        )
        content = self._render_invoice(self.invoice)
        spans = [
            span.text_content()
            for span in content.xpath("//th[@name='th_description']/span")
        ]
        self.assertEqual(spans, ["Product", "Description"])

    def test_invoice_later_condition_on_the_header_span_is_kept(self):
        # A view applied after this module's that adds a condition to the
        # header's span keeps it: this module changes only what the span
        # prints, so the condition also hides "Product"
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.header_span_condition",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="attributes"
                        >
                            <attribute
                                name="t-if"
                                add="o.move_type != 'out_invoice'"
                                separator=" and "
                            />
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, [""])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_later_text_inside_the_header_span_is_not_printed(self):
        # A view applied after this module's that adds a text inside the
        # header's span: the span prints "Product" instead of what it holds, so
        # that text is not printed
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.inside_header_span",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="inside"
                        >
                            <span> (extra)</span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_vendor_bill_header_prints_a_later_text_inside_its_span(self):
        # The same view on a vendor bill, whose header's span prints what it
        # holds
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.inside_header_span",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="inside"
                        >
                            <span> (extra)</span>
                        </xpath>
                    </data>
                """,
            }
        )
        bill = self.init_invoice("in_invoice", products=self.product, post=True)
        headers, cells = self._render_description_column(bill)
        self.assertEqual(headers, ["Description (extra)"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_invoice_later_view_replacing_the_header_span_prints_its_text(self):
        # A view applied after this module's that replaces the header's span
        # prints its own text instead of "Product"
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.header_span",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//th[@name='th_description']/span"
                            position="replace"
                        >
                            <span>Item</span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Item"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_product_line_without_label_prints_nothing(self):
        # The label's span keeps Odoo's condition: as in Odoo, a product line
        # whose label is empty prints nothing
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.invoice_line_ids.name = False
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, [""])

    def test_invoice_line_without_product_prints_its_label(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create({"name": "Delivery", "price_unit": 10.0})
                ]
            }
        )
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet", "Delivery"])

    def test_invoice_line_without_product_or_label_prints_nothing(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write({"invoice_line_ids": [Command.create({"price_unit": 10.0})]})
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet", ""])

    def test_invoice_section_and_note_rows_print_their_text(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create(
                        {"display_type": "line_section", "name": "Bouquets"}
                    ),
                    Command.create(
                        {"display_type": "line_note", "name": "Handle with care"}
                    ),
                ]
            }
        )
        invoice.action_post()
        content = self._render_invoice(invoice)
        rows = [
            " ".join(row.text_content().split())
            for row in content.xpath(
                "//tr[contains(@class, 'o_line_section')"
                " or contains(@class, 'o_line_note')]"
            )
        ]
        self.assertEqual(rows, ["Bouquets", "Handle with care"])
        cells = [
            " ".join(cell.text_content().split())
            for cell in content.xpath("//td[@name='account_invoice_line_name']")
        ]
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_product_column_keeps_what_another_module_adds(self):
        # A view of another module adds a text inside the description cell, as
        # pos_sale does with the products of a point of sale down payment
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.description_cell",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']"
                            position="inside"
                        >
                            <span> and its extra text</span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet and its extra text"])

    def test_invoice_product_line_prints_only_its_product_name(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.invoice_line_ids.name = "[BQ01] Rose bouquet\nWith a ribbon"
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_line_without_product_keeps_the_lines_of_its_label(self):
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create(
                        {"name": "Delivery\nto the church", "price_unit": 10.0}
                    )
                ]
            }
        )
        invoice.action_post()
        cells = self._render_invoice(invoice).xpath(
            "//td[@name='account_invoice_line_name']"
        )
        self.assertEqual(
            [" ".join(cell.text_content().split()) for cell in cells],
            ["Rose bouquet", "Delivery to the church"],
        )
        self.assertEqual([len(cell.xpath(".//br")) for cell in cells], [0, 1])

    def test_invoice_later_view_on_the_label_span_keeps_the_section_title(self):
        # A view applied after this module's that replaces the label's span, as
        # a localization may do, lands on the product line's span, not on the
        # title of a section, and prints its text instead of the product's name.
        # The view has priority 1, as this module's has, and is applied after it
        # because views of one priority apply in the order they were created
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.later_label_span",
                "type": "qweb",
                "priority": 1,
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath expr="//span[@t-field='line.name']" position="replace">
                            <span>Another text</span>
                        </xpath>
                    </data>
                """,
            }
        )
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create({"display_type": "line_section", "name": "Bouquets"})
                ]
            }
        )
        invoice.action_post()
        content = self._render_invoice(invoice)
        sections = [
            " ".join(row.text_content().split())
            for row in content.xpath("//tr[contains(@class, 'o_line_section')]")
        ]
        self.assertEqual(sections, ["Bouquets"])
        spans = content.xpath("//td[@name='account_invoice_line_name']//span")
        self.assertEqual([span.text_content() for span in spans], ["Another text"])

    def test_invoice_earlier_span_ahead_of_the_label_span_keeps_its_text(self):
        # A view applied before this module's, with priority 0, that puts a span
        # ahead of the label's span: this module finds Odoo's span by its
        # t-field, so the new span keeps its text and the product's name follows
        # it
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.earlier_label_span",
                "type": "qweb",
                "priority": 0,
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="before"
                        >
                            <span>(extra) </span>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["(extra) Rose bouquet"])

    def test_invoice_later_condition_on_the_label_span_is_kept(self):
        # A view applied after this module's that adds a condition to the
        # label's span: the span keeps Odoo's condition, and the new one applies
        # with it to every line, a product line included
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_condition",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute
                                name="t-if"
                                add="line.quantity &gt; 1"
                                separator=" and "
                            />
                        </xpath>
                    </data>
                """,
            }
        )
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create({"name": "Delivery", "price_unit": 10.0}),
                ]
            }
        )
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["", ""])

    def test_invoice_later_else_prints_only_where_the_label_span_does_not(self):
        # A view applied after this module's that adds a t-elif and a t-else
        # after the label's span: they print only where the span prints nothing,
        # on a product line without a label and on a line with neither a product
        # nor a label
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_else",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="after"
                        >
                            <span t-elif="line.price_unit &gt; 5">Priced line</span>
                            <span t-else="">No description</span>
                        </xpath>
                    </data>
                """,
            }
        )
        invoice = self.init_invoice("out_invoice", products=self.product)
        invoice.invoice_line_ids.name = False
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create({"product_id": self.product.id}),
                    Command.create({"price_unit": 10.0}),
                    Command.create({"price_unit": 1.0}),
                ]
            }
        )
        invoice.action_post()
        headers, cells = self._render_description_column(invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(
            cells, ["No description", "Rose bouquet", "Priced line", "No description"]
        )

    def test_invoice_later_t_out_on_the_label_span_prints_the_label(self):
        # A view applied after this module's that turns the label's span into a
        # t-out of the label, without its t-field and t-options, prints the
        # label: this module's option goes away with t-options
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_out",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute name="t-field" />
                            <attribute name="t-options" />
                            <attribute name="t-out">line.name</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

    def test_invoice_later_widget_on_the_label_span_prints_the_product(self):
        # A view applied after this module's that changes the widget of the
        # label's span still prints the product's name, in that widget
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_widget",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute name="t-options-widget">'html'</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["Rose bouquet"])

    def test_invoice_later_field_on_the_label_span_prints_that_field(self):
        # A view applied after this module's that makes the label's span print
        # another field of the line prints that field: the option applies to
        # the line's label only
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_field",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute name="t-field">line.move_name</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, [self.invoice.name])

    def test_invoice_later_record_on_the_label_span_prints_its_name(self):
        # A view applied after this module's that makes the label's span print
        # the name of another record, the invoice, prints it: the option
        # applies to a line only
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_record",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute name="t-field">line.move_id.name</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, [self.invoice.name])

    def test_invoice_later_options_on_the_label_span_print_the_label(self):
        # A view applied after this module's that replaces the options of the
        # label's span drops this module's option, so the span prints the label,
        # as Odoo's own span does
        self.env["ir.ui.view"].create(
            {
                "name": "test.report_invoice_document.label_span_options",
                "type": "qweb",
                "inherit_id": self.env.ref("account.report_invoice_document").id,
                "arch": """
                    <data>
                        <xpath
                            expr="//td[@name='account_invoice_line_name']/span"
                            position="attributes"
                        >
                            <attribute name="t-options">{'widget': 'text'}</attribute>
                        </xpath>
                    </data>
                """,
            }
        )
        headers, cells = self._render_description_column(self.invoice)
        self.assertEqual(headers, ["Product"])
        self.assertEqual(cells, ["[BQ01] Rose bouquet"])

# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingHttpCommon


@tagged("post_install", "-at_install")
class TestReportInvoice(AccountTestInvoicingHttpCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.partner_a.email = "partner_a@example.com"

    def test_posted_invoice_preview(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)

        res = self.url_open(invoice.get_portal_url(report_type="html"))

        self.assertIn("INV/2019/00001", res.text)
        self.assertNotIn("PROFORMA", res.text)

    def test_posted_invoice_download(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)

        res = self.url_open(invoice.get_portal_url(report_type="pdf", download=True))

        self.assertIn("INV/2019/00001", res.text)
        self.assertNotIn("PROFORMA", res.text)

    def test_posted_credit_note_preview(self):
        credit_note = self.init_invoice("out_refund", amounts=[1000], post=True)

        res = self.url_open(credit_note.get_portal_url(report_type="html"))

        self.assertIn("RINV/2019/00001", res.text)
        self.assertNotIn("PROFORMA", res.text)

    def test_draft_invoice_preview(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000])

        res = self.url_open(invoice.get_portal_url(report_type="html"))

        self.assertIn("PROFORMA", res.text)

    def test_cancelled_invoice_preview(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)
        invoice.button_cancel()

        res = self.url_open(invoice.get_portal_url(report_type="html"))

        self.assertIn("INV/2019/00001", res.text)
        self.assertIn("PROFORMA", res.text)

    def test_reset_to_draft_invoice_preview(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)
        invoice.button_cancel()
        invoice.button_draft()

        res = self.url_open(invoice.get_portal_url(report_type="html"))

        self.assertIn("INV/2019/00001", res.text)
        self.assertIn("PROFORMA", res.text)

    def test_reset_to_draft_invoice_proforma_filename(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)
        invoice.button_cancel()
        invoice.button_draft()

        self.assertEqual(
            invoice._get_invoice_proforma_pdf_report_filename(),
            "INV_2019_00001_proforma.pdf",
        )

    def test_posted_invoice_send_fallback(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True)
        wizard = (
            self.env["account.move.send"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"mail_template_id": self.env.ref(invoice._get_mail_template()).id})
        )

        def _call_web_service_before_invoice_pdf_render(self, invoices_data):
            for move_data in invoices_data.values():
                move_data["error"] = "service_failed_before"

        with patch.object(
            type(wizard),
            "_call_web_service_before_invoice_pdf_render",
            _call_web_service_before_invoice_pdf_render,
        ):
            wizard.action_send_and_print(allow_fallback_pdf=True)

        attachment = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "account.move"),
                ("res_id", "=", invoice.id),
                ("name", "=", "INV_2019_00001.pdf"),
            ]
        )
        self.assertFalse(invoice.invoice_pdf_report_id)
        self.assertEqual(len(attachment), 1)
        self.assertNotIn(b"PROFORMA", attachment.raw)

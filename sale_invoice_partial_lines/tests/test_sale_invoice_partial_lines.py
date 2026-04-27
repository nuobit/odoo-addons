# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("-at_install", "post_install")
class TestSaleInvoicePartialLines(TestSaleCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.sale_order = (
            cls.env["sale.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": cls.partner_a.id,
                    "partner_invoice_id": cls.partner_a.id,
                    "partner_shipping_id": cls.partner_a.id,
                    "pricelist_id": cls.company_data["default_pricelist"].id,
                    "order_line": [
                        Command.create(
                            {
                                "display_type": "line_section",
                                "name": "Section A",
                            }
                        ),
                        Command.create(
                            {
                                "product_id": cls.company_data["product_order_no"].id,
                                "product_uom_qty": 5,
                                "tax_id": False,
                            }
                        ),
                        Command.create(
                            {
                                "product_id": cls.company_data[
                                    "product_service_order"
                                ].id,
                                "product_uom_qty": 3,
                                "tax_id": False,
                            }
                        ),
                        Command.create(
                            {
                                "display_type": "line_section",
                                "name": "Section B",
                            }
                        ),
                        Command.create(
                            {
                                "product_id": cls.company_data[
                                    "product_delivery_no"
                                ].id,
                                "product_uom_qty": 2,
                                "tax_id": False,
                            }
                        ),
                    ],
                }
            )
        )
        cls.sale_order.action_confirm()
        cls.product_lines = cls.sale_order.order_line.filtered(
            lambda line: not line.display_type
        )
        cls.section_a, cls.section_b = cls.sale_order.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        # Force quantities so every product line is invoiceable
        for line in cls.product_lines:
            line.qty_delivered = line.product_uom_qty
        cls.context = {
            "active_model": "sale.order",
            "active_ids": [cls.sale_order.id],
            "active_id": cls.sale_order.id,
        }

    def _create_wizard(self, only_selected_lines):
        return (
            self.env["sale.advance.payment.inv"]
            .with_context(**self.context)
            .create(
                {
                    "advance_payment_method": "delivered",
                    "only_selected_lines": only_selected_lines,
                }
            )
        )

    def test_count_and_amount_compute(self):
        line_1, line_2, _line_3 = self.product_lines
        line_1.selected = True
        line_2.selected = True
        self.assertEqual(self.sale_order.selected_lines_count, 2)
        self.assertEqual(
            self.sale_order.selected_lines_amount,
            line_1.price_subtotal + line_2.price_subtotal,
        )

    def test_no_marked_lines_raises(self):
        wizard = self._create_wizard(only_selected_lines=True)
        with self.assertRaises(UserError):
            wizard.create_invoices()

    def test_no_selected_invoiceable_lines_keeps_marks(self):
        _line_1, _line_2, line_3 = self.product_lines
        line_3.qty_delivered = 0
        line_3.selected = True
        wizard = self._create_wizard(only_selected_lines=True)
        with self.assertRaises(UserError):
            wizard.create_invoices()
        self.assertTrue(line_3.selected)

    def test_invoice_only_marked_lines(self):
        line_1, line_2, _line_3 = self.product_lines
        line_1.selected = True
        line_2.selected = True
        wizard = self._create_wizard(only_selected_lines=True)
        wizard.create_invoices()
        invoice = self.sale_order.invoice_ids
        self.assertEqual(len(invoice), 1)
        invoiced_so_product_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        ).sale_line_ids
        self.assertEqual(invoiced_so_product_lines, line_1 + line_2)

    def test_marks_reset_after_invoice(self):
        line_1, line_2, _line_3 = self.product_lines
        line_1.selected = True
        line_2.selected = True
        self._create_wizard(only_selected_lines=True).create_invoices()
        self.assertFalse(line_1.selected)
        self.assertFalse(line_2.selected)
        self.assertEqual(self.sale_order.selected_lines_count, 0)

    def test_only_invoiceable_marks_reset_after_invoice(self):
        line_1, _line_2, line_3 = self.product_lines
        line_1.selected = True
        line_3.qty_delivered = 0
        line_3.selected = True
        self._create_wizard(only_selected_lines=True).create_invoices()
        invoice = self.sale_order.invoice_ids
        invoiced_so_product_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        ).sale_line_ids
        self.assertEqual(invoiced_so_product_lines, line_1)
        self.assertFalse(line_1.selected)
        self.assertTrue(line_3.selected)

    def test_only_marked_section_kept(self):
        # Mark only the line under Section B; Section A must be dropped.
        _line_1, _line_2, line_3 = self.product_lines
        line_3.selected = True
        self._create_wizard(only_selected_lines=True).create_invoices()
        invoice = self.sale_order.invoice_ids
        self.assertEqual(len(invoice), 1)
        invoiced_so_product_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        ).sale_line_ids
        self.assertEqual(invoiced_so_product_lines, line_3)
        sections_in_invoice = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "line_section"
        )
        self.assertEqual(sections_in_invoice.mapped("name"), ["Section B"])

    def test_unselected_section_note_dropped(self):
        line_1, line_2, line_3 = self.product_lines
        self.section_a.sequence = 10
        line_1.sequence = 20
        line_2.sequence = 30
        note = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "display_type": "line_note",
                "name": "Unselected section note",
                "sequence": 40,
            }
        )
        self.section_b.sequence = 50
        line_3.sequence = 60
        line_3.selected = True
        self._create_wizard(only_selected_lines=True).create_invoices()
        invoice = self.sale_order.invoice_ids
        sections_in_invoice = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "line_section"
        )
        self.assertEqual(sections_in_invoice.mapped("name"), ["Section B"])
        self.assertNotIn(note.name, invoice.invoice_line_ids.mapped("name"))

    def test_orphan_note_kept_with_selected_product(self):
        # Note before any section, followed by a selected product line: the
        # note must be carried into the invoice with the selected line.
        line_1, _line_2, _line_3 = self.product_lines
        self.section_a.unlink()
        self.section_b.unlink()
        note = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "display_type": "line_note",
                "name": "Orphan note before product",
                "sequence": 5,
            }
        )
        line_1.sequence = 10
        line_1.selected = True
        self._create_wizard(only_selected_lines=True).create_invoices()
        invoice = self.sale_order.invoice_ids
        self.assertIn(note.name, invoice.invoice_line_ids.mapped("name"))

    def test_default_path_invoices_all(self):
        # Without only_selected_lines the wizard behaves exactly like core sale.
        self._create_wizard(only_selected_lines=False).create_invoices()
        invoice = self.sale_order.invoice_ids
        self.assertEqual(len(invoice), 1)
        invoiced_so_product_lines = invoice.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
        ).sale_line_ids
        self.assertEqual(invoiced_so_product_lines, self.product_lines)

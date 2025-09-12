# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestRepairInvoiceNumber(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create a test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'is_company': True,
        })
        
        # Create a test product
        self.product = self.env['product.product'].create({
            'name': 'Test Repair Product',
            'type': 'product',
            'list_price': 100.0,
        })

    def test_repair_invoice_linking(self):
        """Test that repair orders are properly linked to invoices"""
        
        # Create a repair order
        repair_order = self.env['repair.order'].create({
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        # Create an invoice with the repair order name as origin
        invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'invoice_origin': repair_order.name,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })]
        })
        
        # Check that the invoice is linked to the repair order
        self.assertEqual(invoice.repair_order_id, repair_order)
        self.assertEqual(invoice.repair_order_name, repair_order.name)

    def test_manual_repair_linking(self):
        """Test manual linking of repair orders to invoices"""
        
        # Create a repair order
        repair_order = self.env['repair.order'].create({
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_customers').id,
        })
        
        # Create an invoice without origin
        invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })]
        })
        
        # Manually link the repair order to the invoice
        invoice.repair_order_id = repair_order.id
        
        # Check that the linking works
        self.assertEqual(invoice.repair_order_id, repair_order)
        self.assertEqual(invoice.repair_order_name, repair_order.name)
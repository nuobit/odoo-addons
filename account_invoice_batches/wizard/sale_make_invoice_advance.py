# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_batch_create = fields.Boolean(string='Create invoice batch',
                                          default=lambda self: self._count() > 1)

    @api.multi
    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()

        if self.invoice_batch_create:
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            invoices = sale_orders.mapped('invoice_ids')

            if len(invoices) <= 1:
                return res

            invoice_batch = self.env['account.invoice.batch'].create({
                'date': fields.Datetime.now(),
                'invoice_ids': [(6, False, [x.id for x in invoices])]
            })

            for invoice in invoices:
                if invoice.partner_id.invoice_batch_sending_method:
                    invoice.invoice_batch_sending_method = invoice.partner_id.invoice_batch_sending_method
                if invoice.partner_id.invoice_batch_email_partner_id:
                    invoice.invoice_batch_email_partner_id = invoice.partner_id.invoice_batch_email_partner_id

            if self._context.get('open_batch', False):
                action = self.env.ref('account_invoice_batches.account_invoice_batch_action').read()[0]
                action['views'] = [(self.env.ref('account_invoice_batches.account_invoice_batch_view_form').id, 'form')]
                action['res_id'] = invoice_batch.id

                return action

        return res

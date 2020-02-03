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
                                          default=True)

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if invoice:
            batch_id = self.env.context.get('batch_id')
            if batch_id:
                values = {
                    'invoice_batch_id': batch_id,
                }
                if invoice.partner_id.invoice_batch_sending_method:
                    values['invoice_batch_sending_method'] = invoice.partner_id.invoice_batch_sending_method
                if invoice.partner_id.invoice_batch_email_partner_id:
                    values['invoice_batch_email_partner_id'] = invoice.partner_id.invoice_batch_email_partner_id.id

                invoice.write(values)

        return invoice

    @api.multi
    def create_invoices(self):
        if not self.invoice_batch_create:
            return super(SaleAdvancePaymentInv, self).create_invoices()

        invoice_batch = self.env['account.invoice.batch'].create({
            'date': fields.Datetime.now(),
        })

        self = self.with_context(batch_id=invoice_batch.id)
        res = super(SaleAdvancePaymentInv, self).create_invoices()

        invoices = self.env['account.invoice'].search([
            ('invoice_batch_id', '=', invoice_batch.id)
        ])
        if not invoices:
            raise UserError(_('There is no invoiceable line.'))

        if self._context.get('open_batch', False):
            action = self.env.ref('account_invoice_batches.account_invoice_batch_action').read()[0]
            action['views'] = [
                (self.env.ref('account_invoice_batches.account_invoice_batch_view_form').id, 'form')]
            action['res_id'] = invoice_batch.id

            return action

        return res

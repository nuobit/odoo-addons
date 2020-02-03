# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .common import BATCH_SENDING_METHODS


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
        if invoice_ids:
            batch_id = self.env.context.get('batch_id')
            if batch_id:
                for invoice in self.env['account.invoice'].browse(invoice_ids):
                    values = {
                        'invoice_batch_id': batch_id,
                    }
                    if invoice.partner_id.invoice_batch_sending_method:
                        values['invoice_batch_sending_method'] = invoice.partner_id.invoice_batch_sending_method
                    if invoice.partner_id.invoice_batch_email_partner_id:
                        values['invoice_batch_email_partner_id'] = invoice.partner_id.invoice_batch_email_partner_id.id

                    invoice.write(values)

        return invoice_ids

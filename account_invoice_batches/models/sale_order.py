# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _

from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)

        self.env['account.invoice.batch'].create({
            'date': fields.Datetime.now(),
            'invoice_ids': [(6, False, invoice_ids)]
        })

        for invoice in self.env['account.invoice'].browse(invoice_ids):
            if invoice.partner_id.invoice_batch_sending_method:
                invoice.invoice_batch_sending_method = invoice.partner_id.invoice_batch_sending_method
            if invoice.partner_id.invoice_batch_email_partner_id:
                invoice.invoice_batch_email_partner_id_id = invoice.partner_id.invoice_batch_email_partner_id_id

        return invoice_ids

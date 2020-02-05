# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
        if invoice_ids:
            date_invoice = self.env.context.get('date_invoice')
            if date_invoice:
                invoices = self.env['account.invoice'].browse(invoice_ids)
                invoices.write({'date_invoice': date_invoice})

        return invoice_ids

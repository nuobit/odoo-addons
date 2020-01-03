# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .common import BATCH_SENDING_METHODS


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_batch_id = fields.Many2one(comodel_name='account.invoice.batch',
                                       ondelete='restrict', string='Invoice batch',
                                       track_visibility='onchange')
    invoice_batch_sending_method = fields.Selection(selection=BATCH_SENDING_METHODS,
                                                    string='Sending method', track_visibility='onchange')
    invoice_batch_email_partner_id = fields.Many2one(comodel_name='res.partner',
                                                     domain="[('id', 'child_of', partner_id), ('email', '!=', False)]",
                                                     ondelete='restrict',
                                                     string='Contact',
                                                     track_visibility='onchange')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id.invoice_batch_sending_method:
            self.invoice_batch_sending_method = self.partner_id.invoice_batch_sending_method
        if self.partner_id.invoice_batch_email_partner_id:
            self.invoice_batch_email_partner_id = self.partner_id.invoice_batch_email_partner_id

        return res

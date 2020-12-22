# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_ids = fields.One2many(comodel_name='account.asset.asset',
                                inverse_name='invoice_line_id')

    def _prepare_asset_values(self):
        vals = super(AccountInvoiceLine, self)._prepare_asset_values()
        vals['invoice_line_id'] = self.id
        return vals

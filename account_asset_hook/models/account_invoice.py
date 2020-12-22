# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _prepare_asset_values(self):
        vals = {
            'name': self.name,
            'code': self.invoice_id.number or False,
            'category_id': self.asset_category_id.id,
            'value': self.price_subtotal_signed,
            'partner_id': self.invoice_id.partner_id.id,
            'company_id': self.invoice_id.company_id.id,
            'currency_id': self.invoice_id.company_currency_id.id,
            'date': self.invoice_id.date_invoice,
            'invoice_id': self.invoice_id.id,
        }
        vals.update(self.env.context.get('update_asset_values', {}))
        changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
        vals.update(changed_vals['value'])
        return vals

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            vals = self._prepare_asset_values()
            asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        invoice_line_vals = super()._prepare_invoice_line(line, invoice_id)

        if line.tax_ids:
            invoice_line_vals.update({
                'invoice_line_tax_ids': [(6, False, line.tax_ids.mapped('id'))],
            })

        return invoice_line_vals

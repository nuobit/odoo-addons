# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    invoice_line_id = fields.Many2one(comodel_name='account.invoice.line',
                                      ondelete='restrict',
                                      readonly=True)

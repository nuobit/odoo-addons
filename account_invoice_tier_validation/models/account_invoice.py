# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ['account.invoice', 'tier.validation']
    _state_from = ['draft']
    _state_to = ['open']

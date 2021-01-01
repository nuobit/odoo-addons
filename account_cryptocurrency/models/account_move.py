# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import json


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    amount_currency = fields.Monetary(digits=(15, 9))

    @api.multi
    @api.constrains('amount_currency', 'debit', 'credit')
    def _check_currency_amount(self):
        for line in self:
            # If account have a second currency, don't apply constraint
            if line.account_id.currency_id:
                continue
            super(AccountMoveLine, line)._check_currency_amount()

# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    payment_mode_id = fields.Many2one(
        domain=[('payment_type', 'in', ('inbound', 'outbound'))],
    )

    @api.onchange('partner_id', 'journal_id')
    def _onchange_partner_journal_id(self):
        if self.journal_id:
            if self.journal_id.type == 'sale':
                if self.partner_id.customer:
                    self.payment_mode_id = self.partner_id.customer_payment_mode_id.id
                else:
                    self.payment_mode_id = False
            elif self.journal_id.type == 'purchase':
                if self.partner_id.supplier:
                    self.payment_mode_id = self.partner_id.supplier_payment_mode_id.id
                else:
                    self.payment_mode_id = False
        else:
            self.payment_mode_id = False


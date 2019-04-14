# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools.misc import formatLang


class account_journal(models.Model):
    _inherit = "account.journal"

    @api.multi
    def get_journal_dashboard_datas(self):
        res = super(account_journal, self).get_journal_dashboard_datas()

        currency = self.currency_id or self.company_id.currency_id
        account_journal_sum = 0

        if self.type in ['bank', 'cash']:
            account_ids = tuple(filter(None, [self.default_debit_account_id.id, self.default_credit_account_id.id]))
            if account_ids:
                amount_field = 'balance' if (
                        not self.currency_id or self.currency_id == self.company_id.currency_id) else 'amount_currency'
                query = """SELECT sum(%s) FROM account_move_line WHERE account_id in %%s AND journal_id = %%s AND date <= %%s;""" % (
                    amount_field,)
                self.env.cr.execute(query, (account_ids, self.id, fields.Date.today(),))
                query_results = self.env.cr.dictfetchall()
                if query_results and query_results[0].get('sum') != None:
                    account_journal_sum = query_results[0].get('sum')

        res.update({
            'account_journal_balance': formatLang(self.env, currency.round(account_journal_sum) + 0.0,
                                                  currency_obj=currency),
        })

        return res

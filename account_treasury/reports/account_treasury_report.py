# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
#from openerp.osv import fields,osv
from openerp import models, fields, tools
import openerp.addons.decimal_precision as dp

class account_treasury_report2(models.Model):
    _name = "account.treasury.report2"
    _description = "Treasury Analysis2"
    _auto = False

    _order = 'date asc'

    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscalyear', readonly=True)
    period_id = fields.Many2one('account.period', 'Period', readonly=True)
    debit = fields.Float('Debit', readonly=True)
    credit = fields.Float('Credit', readonly=True)
    balance = fields.Float('Balance', readonly=True)
    date = fields.Date('Beginning of Period Date', readonly=True)
    starting_balance = fields.Float(compute='_compute_balances', digits_compute=dp.get_precision('Account'), string='Starting Balance', multi='balance')
    ending_balance = fields.Float(compute='_compute_balances', digits_compute=dp.get_precision('Account'), string='Ending Balance', multi='balance')
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    #@api.depends()
    def _compute_balances(self):
        all_companies = self.env['res.company'].search([])
        current_sum = dict((company.id, 0.0) for company in all_companies)
        for record in self:
            record.starting_balance = current_sum[record.company_id.id]
            current_sum[record.company_id.id] += record.balance
            record.ending_balance = current_sum[record.company_id.id]



    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_treasury_report2')
        cr.execute("""
            create or replace view account_treasury_report2 as (
            select
                p.id as id,
                p.fiscalyear_id as fiscalyear_id,
                p.id as period_id,
                sum(l.debit) as debit,
                sum(l.credit) as credit,
                sum(l.debit-l.credit) as balance,
                p.date_start as date,
                am.company_id as company_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
            where l.state != 'draft'
              and a.type = 'liquidity'
            group by p.id, p.fiscalyear_id, p.date_start, am.company_id
            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

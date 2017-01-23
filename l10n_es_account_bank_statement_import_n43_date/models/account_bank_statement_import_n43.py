# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from datetime import datetime


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    @api.model
    def _parse_file(self, data_file):
        n43 = self._check_n43(data_file)
        if not n43:
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)
        transactions = []
        for group in n43:
            for line in group['lines']:
                conceptos = []
                for concept_line in line['conceptos']:
                    conceptos.extend(x.strip()
                                     for x in line['conceptos'][concept_line]
                                     if x.strip())
                vals_line = {
                    'date': fields.Date.to_string(line['fecha_oper']),
                    'name': ' '.join(conceptos),
                    'ref': self._get_ref(line),
                    'amount': line['importe'],
                    'note': line,
                }
                c = line['conceptos']
                if c.get('01'):
                    vals_line['partner_name'] = c['01'][0] + c['01'][1]
                if not vals_line['name']:
                    vals_line['name'] = vals_line['ref']
                transactions.append(vals_line)
        vals_bank_statement = {
            'transactions': transactions,
            'balance_start': n43 and n43[0]['saldo_ini'] or 0.0,
            'balance_end_real': n43 and n43[-1]['saldo_fin'] or 0.0,
        }
        str_currency = self.journal_id.currency and \
                       self.journal_id.currency.name or \
                       self.journal_id.company_id.currency_id.name
        return str_currency, False, [vals_bank_statement]


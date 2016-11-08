from openerp import models, fields, api, exceptions, _

import logging


logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    """SEPA Direct Debit Mandate"""
    _inherit = 'account.banking.mandate'

    lang = fields.Char(compute='_compute_lang')

    @api.depends('partner_id')
    def _compute_lang(self):
        self.lang = self.partner_id.lang or self.env.lang
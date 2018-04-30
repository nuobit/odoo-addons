from openerp import models, api
from openerp.tools.float_utils import float_round

class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    @api.multi
    def compute_line_amount(self, total_amount, remaining_amount):
        res = super(AccountPaymentTermLine, self).compute_line_amount(total_amount, remaining_amount)

        prec = self.env['decimal.precision'].precision_get('Account')
        if self.value == 'fixed' and total_amount < 0:
            return float_round(-self.value_amount, precision_digits=prec)
        else:
            return res

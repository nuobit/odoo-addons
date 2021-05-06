# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _check_null_depreciations(self, cat):
        return True

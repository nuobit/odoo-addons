# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_taxes_values(self):
        res = super(AccountInvoice, self).get_taxes_values()

        bmap = {"False": False, "True": True}
        for key, _val in res.items():
            _, _, _, res[key]["origin_account_analytic_id"] = [
                x not in bmap and int(x) or bmap[x] for x in key.split("-")
            ]

        return res

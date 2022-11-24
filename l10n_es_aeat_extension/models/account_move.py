# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_aeat_tax_base_info(self, res, tax, line, sign):
        taxes = tax.amount_type == "group" and tax.children_tax_ids or tax
        for tax in taxes:
            super()._get_aeat_tax_base_info(res, tax, line, sign)

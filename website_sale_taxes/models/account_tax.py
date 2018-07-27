# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def _get_tax_by_group(self, only_website=True):
        res = {}
        for tax in self:
            if only_website and not tax.tax_group_id.show_on_website:
                continue
            res.setdefault(tax.tax_group_id, {'name': tax.tax_group_id.name, 'amount': 0.0})
            res[tax.tax_group_id]['amount'] += tax.amount

        res = sorted(res.items(), key=lambda l: l[0].sequence)

        return res

class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    show_on_website = fields.Boolean(string="Show on website", default=False)
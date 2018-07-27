# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_tax_amount_by_group(self, only_website=True):
        self.ensure_one()
        res = {}
        currency = self.currency_id or self.company_id.currency_id

        price_reduce = self.price_unit * (1.0 - self.discount / 100.0)
        taxes = self.tax_id.compute_all(price_reduce, quantity=self.product_uom_qty,
                                        product=self.product_id, partner=self.order_id.partner_shipping_id)['taxes']
        for tax in self.tax_id:
            if only_website and not tax.tax_group_id.show_on_website:
                continue
            res.setdefault(tax.tax_group_id, 0.0)
            for t in taxes:
                if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                    res[tax.tax_group_id] += t['amount']

        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = map(lambda l: (l[0].name, l[1]), res)

        return res

# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _

import re


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_amounts(self):
        self.ensure_one()
        price = self.sale_line_id.price_unit * (1 - (self.sale_line_id.discount or 0.0) / 100.0)
        taxes = self.sale_line_id.tax_id.compute_all(price, self.sale_line_id.order_id.currency_id,
                                                     self.quantity_done, product=self.product_id,
                                                     partner=self.picking_id.partner_id)
        return {
            'tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            'total': taxes['total_included'],
            'subtotal': taxes['total_excluded'],
        }

    def get_line_lots(self):
        if self.product_id.tracking in ('lot', 'serial'):
            return self.mapped('move_line_ids.lot_id') \
                .sorted(lambda x: x.name).mapped('name')

        return None

    def _extract_product_code(self, name):
        m = re.match(r'^ *\[([^]]+)\] *(.*)$', name, flags=re.DOTALL)
        if not m:
            return None, name

        return m.groups()

    def get_product_codes(self):
        default_code = self.product_id.default_code or None
        customer_ref = None
        buyer = self.product_id.buyer_ids.filtered(lambda x: x.partner_id == self.picking_id.partner_id)
        if buyer and buyer.code:
            customer_ref = buyer.code

        return default_code, customer_ref

    def get_splited_line_description(self):
        if not self.product_id:
            return self.name

        line_partner_ref, line_name = self._extract_product_code(self.name)
        default_code, customer_ref = self.get_product_codes()
        if line_partner_ref:
            if default_code:
                if line_partner_ref == default_code:
                    return line_name

            if customer_ref:
                if line_partner_ref == customer_ref:
                    return line_name

        return self.name

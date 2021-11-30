# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import re


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_uom_rate_conversion(self, uom_from, uom_to):
        def _get_uom_rate(uom):
            uom_rate = uom.factor_inv
            if uom.uom_type == 'smaller':
                uom_rate = 1 / uom_rate

            return uom_rate

        if uom_from == uom_to:
            return 1

        if uom_from.category_id != uom_to.category_id:
            raise UserError(_("Cannot convert the units of the product %s") % (
                    self.product_id.default_code or self.product_id.name))

        return _get_uom_rate(uom_from) / _get_uom_rate(uom_to)

    sale_price_unit = fields.Float("Sale unit price", compute="_compute_sale_price_unit",
                                   digits=dp.get_precision('Product Price'))

    def _compute_sale_price_unit(self):
        for rec in self:
            factor_rate = rec._get_uom_rate_conversion(
                rec.sale_line_id.product_uom, rec.product_uom)
            rec.sale_price_unit = rec.sale_line_id.price_unit / factor_rate * \
                                  (1 - (rec.sale_line_id.discount or 0.0) / 100.0)

    def _get_amounts(self):
        self.ensure_one()
        taxes = self.sale_line_id.tax_id.compute_all(
            self.sale_price_unit, self.sale_line_id.order_id.currency_id,
            self.quantity_done, product=self.product_id, partner=self.picking_id.partner_id)
        return {
            'tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            'total': taxes['total_included'],
            'subtotal': taxes['total_excluded'],
        }

    def get_line_lots(self):
        if self.product_id.tracking in ('lot', 'serial'):
            lots = []
            for l in self.move_line_ids:
                qty = {'assigned': l.product_qty, 'done': l.qty_done}
                if l.state in qty:
                    lots.append("%s (%s %s)" % (l.lot_id.name, str(qty[l.state]), l.product_uom_id.name))
            return lots
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

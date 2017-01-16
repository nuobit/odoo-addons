# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_delivery_line(self, carrier, price_unit):
        if price_unit != 0.0:
            sol = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        else:
            sol = False

        return sol



class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    fixed_price_without_taxes = fields.Boolean(string='Price without taxes', default=False)

    @api.multi
    def create_price_rules(self):
        res = super(DeliveryCarrier, self).create_price_rules()

        PriceRule = self.env['delivery.price.rule']
        for record in self:
            if record.delivery_type == 'fixed' and self.fixed_price_without_taxes:
                prs = PriceRule.search([('carrier_id', '=', record.id)])
                for pr in prs:
                    pr.variable = 'price_untaxed'

        return res

    @api.multi
    def get_price_available(self, order):
        self.ensure_one()
        total = weight = volume = quantity = 0
        total_delivery = total_delivery_untaxed = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery_untaxed += line.price_subtotal
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty

        total_untaxed = (order.amount_untaxed or 0.0) - total_delivery_untaxed
        total_untaxed = order.currency_id.with_context(date=order.date_order).compute(total_untaxed, order.company_id.currency_id)

        total = (order.amount_total or 0.0) - total_delivery
        total = order.currency_id.with_context(date=order.date_order).compute(total, order.company_id.currency_id)

        return self.get_price_from_picking(total_untaxed, total, weight, volume, quantity)

    def get_price_from_picking(self, total_untaxed, total, weight, volume, quantity):
        price = 0.0
        criteria_found = False
        price_dict = {'price_untaxed': total_untaxed, 'price': total, 'volume': volume,
                      'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(_("Selected product in the delivery method doesn't fulfill any of the delivery carrier(s) criteria."))

        return price



class PriceRule(models.Model):
    _inherit = "delivery.price.rule"

    variable = fields.Selection(selection_add=[('price_untaxed', 'Price untaxed')], default='price_untaxed')
    variable_factor = fields.Selection(selection_add=[('price_untaxed', 'Price untaxed')])

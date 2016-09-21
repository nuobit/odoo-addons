# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id, group_id):
        res = super(purchase_order, self)._prepare_order_line_move(order, order_line, picking_id, group_id)

        if order.location_id.usage == 'customer':
            name9 = order_line.product_id.with_context(
                 dict(self._context or {}, lang=order.dest_address_id.lang)).display_name

            for olm in res:
                olm['name'] = name9

        return res

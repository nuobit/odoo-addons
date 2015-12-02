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

from openerp import api, models, fields, SUPERUSER_ID
from openerp.api import Environment



import logging

_logger = logging.getLogger(__name__)



class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        tx = None
        res = super(PaymentTransaction, self).form_feedback(cr, uid, data, acquirer_name, context=context)

        # fetch the tx, check its state, confirm the potential SO
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(cr, uid, data, context=context)

        if tx and tx.state == 'done' and tx.sale_order_id and tx.sale_order_id.state in ['draft', 'sent']:
            tx.sale_order_id.action_button_confirm(context=dict(context, send_email=True))
            tx.sale_order_id.picking_ids.action_assign()
        elif tx and tx.state in ['cancel', 'error'] and tx.sale_order_id and tx.sale_order_id.state in ['draft']:
            tx.sale_order_id.action_cancel()

        return res
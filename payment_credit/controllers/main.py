# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons import website_sale

_logger = logging.getLogger(__name__)


class CreditController(http.Controller):
    _accept_url = '/payment/credit/feedback'

    @http.route([
        '/payment/credit/feedback',
    ], type='http', auth='none', csrf=False)
    def credit_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'credit')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))


class WebsiteSale(website_sale.controllers.main.WebsiteSale):
    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        res = super(WebsiteSale, self).payment_get_status(sale_order_id, **post)

        tx_obj = request.env['sale.order'].browse(sale_order_id).payment_tx_id
        if tx_obj.acquirer_id.provider == 'credit':
            if tx_obj.state == 'done':
                # message = '<p>%s</p>' % _('Your payment has been received.')
                res['message'] = None

        return res